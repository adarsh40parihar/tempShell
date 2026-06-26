import logging
import traceback
from datetime import datetime

from fastapi import HTTPException

from models.user import UserCreate, UserLogin, Token
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from utils.database import Database

logger = logging.getLogger(__name__)


def signup(user: UserCreate) -> dict:
    """Register a new user. Raises HTTPException on failure."""
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (user.username, user.email),
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username or email already taken")

        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (user.username, hash_password(user.password), user.email),
        )
        conn.commit()
        logger.info(f"New user registered: {user.username}")
        return {"message": "Account created", "username": user.username}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")
    finally:
        cursor.close()
        conn.close()


def login(user: UserLogin) -> Token:
    """Authenticate a user and return JWT tokens."""
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, username, password, is_active, failed_login_attempts, locked_until "
            "FROM users WHERE username = %s",
            (user.username,),
        )
        db_user = cursor.fetchone()

        if not db_user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        if db_user["locked_until"] and db_user["locked_until"] > datetime.utcnow():
            raise HTTPException(status_code=403, detail="Account is temporarily locked")

        if not verify_password(user.password, db_user["password"]):
            cursor.execute(
                "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = %s",
                (db_user["id"],),
            )
            conn.commit()
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        if not db_user["is_active"]:
            raise HTTPException(status_code=403, detail="Account is disabled")

        cursor.execute(
            "UPDATE users SET last_login = %s, failed_login_attempts = 0, locked_until = NULL WHERE id = %s",
            (datetime.utcnow(), db_user["id"]),
        )
        conn.commit()

        logger.info(f"User logged in: {user.username}")
        return Token(
            access_token=create_access_token(user.username),
            refresh_token=create_refresh_token(user.username),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Login failed: {e}")
    finally:
        cursor.close()
        conn.close()


def get_me(username: str) -> dict:
    return {"username": username, "authenticated": True}
