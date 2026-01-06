"""
Admin management routes.
MASTER_ADMIN only operations for creating, blocking, and managing admins.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from models.admin import (
    AdminCreate,
    AdminUpdate,
    AdminResponse,
    AdminBlockRequest
)
from core.dependencies import require_role, get_current_admin
from core.security import hash_password
from services.database import DatabaseService

router = APIRouter()

@router.post("/create", response_model=AdminResponse)
async def create_admin(
    admin_data: AdminCreate,
    current_admin: dict = Depends(require_role("MASTER_ADMIN"))
):
    """
    Create a new admin.
    Only MASTER_ADMIN can create admins.
    """
    db_service = DatabaseService()
    
    # Check if email already exists
    existing = db_service.get_admin_by_email(admin_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin with this email already exists"
        )
    
    # Hash password
    password_hash = hash_password(admin_data.password)
    
    # Prepare admin document
    admin_doc = {
        "email": admin_data.email,
        "password_hash": password_hash,
        "name": admin_data.name,
        "role": admin_data.role,
        "permissions": admin_data.permissions or [],
        "status": "active"
    }
    
    # Create admin
    try:
        admin_id = db_service.create_admin(admin_doc)
        admin = db_service.get_admin_by_id(admin_id)
        
        return AdminResponse(
            id=str(admin.get("id")),
            email=admin.get("email"),
            name=admin.get("name"),
            role=admin.get("role"),
            status=admin.get("status"),
            permissions=admin.get("permissions", []),
            created_at=admin.get("created_at"),
            updated_at=admin.get("updated_at")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/block")
async def block_admin(
    request: AdminBlockRequest,
    current_admin: dict = Depends(require_role("MASTER_ADMIN"))
):
    """
    Block or unblock an admin.
    Only MASTER_ADMIN can block admins.
    """
    db_service = DatabaseService()
    
    # Prevent blocking yourself
    if request.admin_id == str(current_admin.get("id")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block your own account"
        )
    
    # Prevent blocking MASTER_ADMIN
    target_admin = db_service.get_admin_by_id(request.admin_id)
    if not target_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    if target_admin.get("role") == "MASTER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot block MASTER_ADMIN"
        )
    
    # Block/unblock admin
    success = db_service.block_admin(request.admin_id, request.blocked)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return {
        "success": True,
        "message": f"Admin {'blocked' if request.blocked else 'unblocked'} successfully"
    }

@router.get("", response_model=List[AdminResponse])
async def get_all_admins(
    skip: int = 0,
    limit: int = 100,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get all admins (paginated).
    All authenticated admins can view this.
    """
    db_service = DatabaseService()
    admins = db_service.get_all_admins(skip=skip, limit=limit)
    
    result = []
    for admin in admins:
        result.append(AdminResponse(
            id=str(admin.get("id")),
            email=admin.get("email"),
            name=admin.get("name"),
            role=admin.get("role"),
            status=admin.get("status"),
            permissions=admin.get("permissions", []),
            created_at=admin.get("created_at"),
            updated_at=admin.get("updated_at")
        ))
    
    return result

@router.delete("/{admin_id}")
async def delete_admin(
    admin_id: str,
    current_admin: dict = Depends(require_role("MASTER_ADMIN"))
):
    """
    Delete an admin (soft delete).
    Only MASTER_ADMIN can delete admins.
    """
    db_service = DatabaseService()
    
    # Prevent deleting yourself
    if admin_id == str(current_admin.get("id")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Prevent deleting MASTER_ADMIN
    target_admin = db_service.get_admin_by_id(admin_id)
    if not target_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    if target_admin.get("role") == "MASTER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete MASTER_ADMIN"
        )
    
    # Delete admin (soft delete)
    success = db_service.delete_admin(admin_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return {
        "success": True,
        "message": "Admin deleted successfully"
    }

