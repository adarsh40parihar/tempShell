from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=63)
    password: str = Field(..., min_length=8, max_length=70)
    email: EmailStr

    @validator("username")
    def username_valid(cls, v):
        if not re.match(r"^[A-Za-z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v.lower()


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
