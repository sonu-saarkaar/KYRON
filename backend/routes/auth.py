"""
Authentication routes for KYRON Admin Panel.
Handles login, logout, and token refresh.
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer
from typing import Optional

from models.admin import LoginRequest, LoginResponse, RefreshTokenRequest, TokenResponse, AdminResponse
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    extract_token_from_header,
    mask_sensitive_data
)
from core.dependencies import get_current_admin
from services.database import DatabaseService
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, http_request: Request):
    """
    Admin login endpoint.
    Creates access and refresh tokens, logs login attempt.
    """
    db_service = DatabaseService()
    
    # Get admin by email
    admin = db_service.get_admin_by_email(request.email)
    
    if not admin:
        # Log failed login attempt
        db_service.create_login_log({
            "admin_id": None,
            "admin_email": mask_sensitive_data(request.email),
            "ip_address": http_request.client.host if http_request.client else "unknown",
            "user_agent": http_request.headers.get("user-agent", "unknown"),
            "success": False,
            "reason": "Invalid email"
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if admin is blocked
    if admin.get("status") != "active":
        db_service.create_login_log({
            "admin_id": str(admin.get("id")),
            "admin_email": mask_sensitive_data(admin.get("email")),
            "ip_address": http_request.client.host if http_request.client else "unknown",
            "user_agent": http_request.headers.get("user-agent", "unknown"),
            "success": False,
            "reason": "Account blocked"
        })
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is blocked"
        )
    
    # Verify password
    if not verify_password(request.password, admin.get("password_hash")):
        db_service.create_login_log({
            "admin_id": str(admin.get("id")),
            "admin_email": mask_sensitive_data(admin.get("email")),
            "ip_address": http_request.client.host if http_request.client else "unknown",
            "user_agent": http_request.headers.get("user-agent", "unknown"),
            "success": False,
            "reason": "Invalid password"
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    admin_id = str(admin.get("id"))
    token_data = {
        "sub": admin_id,
        "role": admin.get("role", "VIEWER"),
        "email": admin.get("email")
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Log successful login
    db_service.create_login_log({
        "admin_id": admin_id,
        "admin_email": admin.get("email"),
        "ip_address": http_request.client.host if http_request.client else "unknown",
        "user_agent": http_request.headers.get("user-agent", "unknown"),
        "device_info": http_request.headers.get("user-agent", "unknown"),
        "success": True
    })
    
    # Prepare admin response (exclude password_hash)
    admin_response = AdminResponse(
        id=admin_id,
        email=admin.get("email"),
        name=admin.get("name"),
        role=admin.get("role", "VIEWER"),
        status=admin.get("status", "active"),
        permissions=admin.get("permissions", []),
        created_at=admin.get("created_at"),
        updated_at=admin.get("updated_at")
    )
    
    return LoginResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        refresh_token=refresh_token,
        admin=admin_response
    )

@router.post("/logout")
async def logout(admin: dict = Depends(get_current_admin)):
    """
    Admin logout endpoint.
    In production, you might want to blacklist the token.
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token, token_type="refresh")
        admin_id = payload.get("sub")
        
        if not admin_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get admin to verify still exists and active
        db_service = DatabaseService()
        admin = db_service.get_admin_by_id(admin_id)
        
        if not admin or admin.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin not found or inactive"
            )
        
        # Create new tokens
        token_data = {
            "sub": admin_id,
            "role": admin.get("role", "VIEWER"),
            "email": admin.get("email")
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}"
        )

@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(admin: dict = Depends(get_current_admin)):
    """
    Get current authenticated admin information.
    """
    return AdminResponse(
        id=str(admin.get("id")),
        email=admin.get("email"),
        name=admin.get("name"),
        role=admin.get("role", "VIEWER"),
        status=admin.get("status", "active"),
        permissions=admin.get("permissions", []),
        created_at=admin.get("created_at"),
        updated_at=admin.get("updated_at")
    )

