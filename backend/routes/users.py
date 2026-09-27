"""
User management routes.
View and manage KYRON users.
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from core.dependencies import get_current_admin
from services.database import DatabaseService

router = APIRouter()

@router.get("")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get all users (paginated).
    All authenticated admins can view users.
    """
    db_service = DatabaseService()
    users = db_service.get_all_users(skip=skip, limit=limit)
    
    # Remove sensitive data
    for user in users:
        if "password_hash" in user:
            del user["password_hash"]
    
    return {
        "success": True,
        "users": users,
        "total": db_service.count_users(),
        "skip": skip,
        "limit": limit
    }

