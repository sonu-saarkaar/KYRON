"""
Pydantic models for Log operations.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class LoginLogResponse(BaseModel):
    """Model for login log response"""
    id: str
    admin_id: str
    admin_email: str
    ip_address: str
    user_agent: str
    device_info: Optional[str] = None
    success: bool
    timestamp: datetime

class AgentLogResponse(BaseModel):
    """Model for agent log response"""
    id: str
    user_id: Optional[str] = None
    action: str
    form_type: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ErrorLogResponse(BaseModel):
    """Model for error log response"""
    id: str
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime

class LogsListResponse(BaseModel):
    """Model for paginated logs response"""
    logs: list
    total: int
    skip: int
    limit: int

