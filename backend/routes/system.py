"""
System management routes.
Control KYRON agent and system settings.
MASTER_ADMIN only operations.
"""

from fastapi import APIRouter, Depends

from models.system import SystemStatusResponse, AgentToggleRequest, SystemSettingsResponse
from core.dependencies import require_role, get_current_admin
from services.database import DatabaseService

router = APIRouter()

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(current_admin: dict = Depends(get_current_admin)):
    """
    Get system status and dashboard statistics.
    All authenticated admins can view system status.
    """
    db_service = DatabaseService()
    
    agent_enabled = db_service.get_agent_status()
    total_users = db_service.count_users()
    total_admins = db_service.count_admins()
    agent_actions_today = db_service.count_agent_logs_today()
    errors_today = db_service.count_error_logs_today()
    
    return SystemStatusResponse(
        agent_enabled=agent_enabled,
        total_users=total_users,
        total_admins=total_admins,
        agent_actions_today=agent_actions_today,
        errors_today=errors_today
    )

@router.post("/agent-toggle")
async def toggle_agent(
    request: AgentToggleRequest,
    current_admin: dict = Depends(require_role("MASTER_ADMIN"))
):
    """
    Toggle KYRON agent ON/OFF.
    Only MASTER_ADMIN can toggle agent.
    """
    db_service = DatabaseService()
    
    db_service.set_agent_status(request.enabled)
    
    return {
        "success": True,
        "message": f"Agent {'enabled' if request.enabled else 'disabled'} successfully",
        "agent_enabled": request.enabled
    }

@router.get("/settings", response_model=SystemSettingsResponse)
async def get_system_settings(
    current_admin: dict = Depends(require_role("MASTER_ADMIN"))
):
    """
    Get all system settings.
    Only MASTER_ADMIN can view system settings.
    """
    db_service = DatabaseService()
    settings = db_service.get_all_settings()
    
    return SystemSettingsResponse(settings=settings)

@router.post("/settings")
async def update_system_settings(
    settings_data: dict,
    current_admin: dict = Depends(require_role("MASTER_ADMIN"))
):
    """
    Update system settings.
    Only MASTER_ADMIN can update system settings.
    """
    db_service = DatabaseService()
    
    for key, value in settings_data.items():
        db_service.set_system_setting(key, value)
    
    return {
        "success": True,
        "message": "Settings updated successfully"
    }

