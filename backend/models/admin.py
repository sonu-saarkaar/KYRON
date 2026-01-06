"""
Pydantic models for Admin operations.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class AdminCreate(BaseModel):
    """Model for creating a new admin"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)
    role: str = Field(default="VIEWER", pattern="^(MASTER_ADMIN|SUPER_ADMIN|ADMIN|OPERATOR|VIEWER)$")
    permissions: Optional[List[str]] = []

class AdminUpdate(BaseModel):
    """Model for updating an admin"""
    name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(MASTER_ADMIN|SUPER_ADMIN|ADMIN|OPERATOR|VIEWER)$")
    permissions: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(active|blocked|deleted)$")

class AdminResponse(BaseModel):
    """Model for admin response"""
    id: str
    email: str
    name: str
    role: str
    status: str
    permissions: List[str]
    created_at: datetime
    updated_at: datetime

class AdminBlockRequest(BaseModel):
    """Model for blocking/unblocking an admin"""
    admin_id: str
    blocked: bool = True

class LoginRequest(BaseModel):
    """Model for admin login"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """Model for login response"""
    success: bool
    message: str
    access_token: str
    refresh_token: str
    admin: AdminResponse

class RefreshTokenRequest(BaseModel):
    """Model for refresh token request"""
    refresh_token: str

class TokenResponse(BaseModel):
    """Model for token response"""
    access_token: str
    refresh_token: str

