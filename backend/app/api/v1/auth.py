from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import UserCreate, UserLogin, Token
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.db.database import Database
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=dict)
async def signup(user: UserCreate):
    """
    Register a new user
    
    - **username**: Alphanumeric username (3-63 characters)
    - **password**: Strong password (min 8 chars, upper, lower, digit, special)
    - **email**: Valid email address
    """
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user already exists
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (user.username, user.email)
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Hash password with bcrypt
        hashed_password = get_password_hash(user.password)
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (user.username, hashed_password, user.email)
        )
        conn.commit()
        
        logger.info(f"New user registered: {user.username}")
        return {
            "message": "User registered successfully",
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error for {user.username}: {e}")
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )
    finally:
        cursor.close()
        conn.close()

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """
    Authenticate user and return JWT tokens
    
    - **username**: User's username
    - **password**: User's password
    """
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fetch user from database
        cursor.execute(
            "SELECT id, username, password, is_active, failed_login_attempts, locked_until FROM users WHERE username = %s",
            (user.username,)
        )
        db_user = cursor.fetchone()
        
        # Check if user exists
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Check if account is locked
        if db_user['locked_until'] and db_user['locked_until'] > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is temporarily locked. Please try again later."
            )
        
        # Verify password
        if not verify_password(user.password, db_user['password']):
            # Increment failed login attempts
            failed_attempts = db_user['failed_login_attempts'] + 1
            cursor.execute(
                "UPDATE users SET failed_login_attempts = %s WHERE id = %s",
                (failed_attempts, db_user['id'])
            )
            conn.commit()
            
            logger.warning(f"Failed login attempt for user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Check if account is active
        if not db_user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled. Please contact support."
            )
        
        # Reset failed login attempts and update last login
        cursor.execute(
            "UPDATE users SET last_login = %s, failed_login_attempts = 0, locked_until = NULL WHERE id = %s",
            (datetime.utcnow(), db_user['id'])
        )
        conn.commit()
        
        # Create JWT tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_password_hash)):
    """Get current user information"""
    return {
        "username": current_user["username"],
        "authenticated": True
    }
