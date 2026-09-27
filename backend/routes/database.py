"""
Database Health and Management Routes
"""

from fastapi import APIRouter, Header
from auth_utils import verify_token
from services.database_manager import get_database_manager

router = APIRouter()

@router.get("/health")
def database_health(authorization: str = Header(None)):
    """Get database health status"""
    verify_token(authorization)
    
    db_manager = get_database_manager()
    health = db_manager.health_check()
    
    return {
        "success": True,
        "health": health
    }

