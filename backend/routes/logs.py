"""
Log management routes.
View login logs, agent logs, and error logs.
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta

from models.logs import LogsListResponse
from core.dependencies import get_current_admin, require_permission
from services.database import DatabaseService

router = APIRouter()

@router.get("/login", response_model=LogsListResponse)
async def get_login_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_id: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get login logs.
    All authenticated admins can view login logs.
    """
    db_service = DatabaseService()
    
    # Only MASTER_ADMIN can view logs for specific admin
    if admin_id and current_admin.get("role") != "MASTER_ADMIN":
        admin_id = None
    
    logs = db_service.get_login_logs(skip=skip, limit=limit, admin_id=admin_id)
    
    return LogsListResponse(
        logs=logs,
        total=len(logs),  # In production, get actual total count
        skip=skip,
        limit=limit
    )

@router.get("/agent", response_model=LogsListResponse)
async def get_agent_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    days: int = Query(7, ge=1, le=30),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get agent logs.
    All authenticated admins can view agent logs.
    """
    db_service = DatabaseService()
    
    # Filter by date
    date_filter = datetime.utcnow() - timedelta(days=days)
    
    logs = db_service.get_agent_logs(skip=skip, limit=limit, date_filter=date_filter)
    
    return LogsListResponse(
        logs=logs,
        total=len(logs),
        skip=skip,
        limit=limit
    )

@router.get("/error", response_model=LogsListResponse)
async def get_error_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    days: int = Query(7, ge=1, le=30),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get error logs.
    All authenticated admins can view error logs.
    """
    db_service = DatabaseService()
    
    # Filter by date
    date_filter = datetime.utcnow() - timedelta(days=days)
    
    logs = db_service.get_error_logs(skip=skip, limit=limit, date_filter=date_filter)
    
    return LogsListResponse(
        logs=logs,
        total=len(logs),
        skip=skip,
        limit=limit
    )

