from datetime import datetime, timezone 
from typing import Optional
import re 
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: UserRole = Field(default=UserRole.viewer)

    @field_validator('password')
    @classmethod 
    def validate(cls, value: str) -> str:
        pattern = re.compile(r"(?.*[A-Za-z])(?=.*\d).{8, }")
        if not pattern.fullmatch(value):
            raise ValueError('Password must contain at least one letter and one digit')
        return value 
    
class UserLogin(UserBase):
    password: str 

class UserRead(UserBase):
    id: int 
    role: UserRole
    is_active: bool 
    created_at: datetime


