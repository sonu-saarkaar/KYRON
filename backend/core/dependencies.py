"""
Dependency injection for FastAPI routes.
Provides authentication and authorization dependencies.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import settings
from core.security import verify_token, extract_token_from_header
from services.database import DatabaseService

# HTTP Bearer token scheme
security = HTTPBearer()

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated admin from JWT token.
    
    Returns:
        Admin document from database
        
    Raises:
        HTTPException: If token is invalid or admin not found
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get admin from database
    db_service = DatabaseService()
    admin = db_service.get_admin_by_id(admin_id)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found"
        )
    
    # Check if admin is blocked
    if admin.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is blocked or inactive"
        )
    
    return admin

def require_role(min_role: str):
    """
    Dependency factory to require minimum role level.
    
    Args:
        min_role: Minimum required role (e.g., "MASTER_ADMIN")
        
    Returns:
        Dependency function that checks role
    """
    min_role_level = settings.ROLES.get(min_role, 0)
    
    async def role_checker(admin: dict = Depends(get_current_admin)) -> dict:
        admin_role = admin.get("role", "")
        admin_role_level = settings.ROLES.get(admin_role, 0)
        
        if admin_role_level < min_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {min_role} role or higher"
            )
        
        return admin
    
    return role_checker

def require_permission(permission: str):
    """
    Dependency factory to require specific permission.
    
    Args:
        permission: Required permission (e.g., "admin.create")
        
    Returns:
        Dependency function that checks permission
    """
    async def permission_checker(admin: dict = Depends(get_current_admin)) -> dict:
        admin_role = admin.get("role", "")
        role_permissions = settings.ROLE_PERMISSIONS.get(admin_role, [])
        
        if permission not in role_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return admin
    
    return permission_checker

# Common dependencies
RequireMasterAdmin = Depends(require_role("MASTER_ADMIN"))
RequireSuperAdmin = Depends(require_role("SUPER_ADMIN"))
RequireAdmin = Depends(require_role("ADMIN"))

