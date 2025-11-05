from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re

class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=63)
    password: str = Field(..., min_length=8, max_length=72)  # Bcrypt limitation
    email: EmailStr
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[A-Za-z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v.lower()
    
    @validator('password')
    def password_strength(cls, v):
        """Enforce NIST password guidelines"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check byte length for bcrypt (72 bytes max)
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes in UTF-8)')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    """Schema for token refresh"""
    refresh_token: str

class CommandExecute(BaseModel):
    """Schema for command execution"""
    command: str = Field(..., max_length=1000, min_length=1)
    
    @validator('command')
    def validate_command(cls, v):
        """Validate and sanitize commands - block dangerous operations"""
        # Strip leading/trailing whitespace
        v = v.strip()
        
        # Block dangerous command patterns
        dangerous_patterns = [
            r'rm\s+-rf\s+/',  # Recursive force delete from root
            r':\(\)\{.*\};:',  # Fork bomb
            r'mkfs',  # Format filesystem
            r'dd\s+if=/dev/zero',  # Disk wipe
            r'>\s*/dev/sd',  # Write to disk
            r'chmod\s+-R\s+777',  # Dangerous permissions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Command contains potentially dangerous operations')
        
        return v

class CommandResponse(BaseModel):
    """Schema for command execution response"""
    output: str
    exit_code: int
    executed_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ShellStatus(BaseModel):
    """Schema for shell status"""
    pod_id: Optional[str]
    status: str
    created_at: Optional[datetime]

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None
