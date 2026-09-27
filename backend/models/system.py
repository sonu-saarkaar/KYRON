"""
Pydantic models for System operations.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel

class SystemStatusResponse(BaseModel):
    """Model for system status response"""
    agent_enabled: bool
    total_users: int
    total_admins: int
    agent_actions_today: int
    errors_today: int

class AgentToggleRequest(BaseModel):
    """Model for toggling agent status"""
    enabled: bool

class SystemSettingsResponse(BaseModel):
    """Model for system settings response"""
    settings: Dict[str, Any]

