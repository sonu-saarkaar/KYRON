"""
This file handles AI Agent operations.
It manages agent status, helper installation state, and activity logs.

Agent States:
- inactive: Agent is not active (default state)
- waiting: Agent is waiting for service request (floating logo visible)
- active: Agent is actively executing a service request
- paused: Agent execution is paused (waiting for user input like OTP)
"""

from fastapi import APIRouter, HTTPException, Header
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from auth_utils import verify_token

# Create router for agent endpoints
router = APIRouter()

# Temporary in-memory storage
agent_status_db = {}  # {user_id: "inactive" | "waiting" | "active" | "paused"}
helper_installed_db = {}  # {user_id: True | False}
activity_db = {}  # {user_id: [{action, description, timestamp}]}
heartbeat_db = {}  # {user_id: last_heartbeat_timestamp} - tracks extension presence

class ActivityLog(BaseModel):
    action: str
    description: str

@router.post("/activate")
def activate_agent(authorization: str = Header(None)):
    """
    Activate the AI agent for the current user.
    (Legacy endpoint - sets state to "waiting" for backward compatibility)
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Set agent state to waiting (new state system)
    # "waiting" means extension is visible and ready for service request
    agent_status_db[user_id] = "waiting"
    
    # Log the activation
    if user_id not in activity_db:
        activity_db[user_id] = []
    
    activity_db[user_id].append({
        "action": "agent_activated",
        "description": "AI Agent activated successfully (state: waiting)",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "message": "Agent activated successfully",
        "status": "waiting",  # Updated to use new state system
        "state": "waiting"  # Also return as "state" for consistency
    }

@router.post("/deactivate")
def deactivate_agent(authorization: str = Header(None)):
    """
    Deactivate the AI agent for the current user.
    (Legacy endpoint - sets state to "inactive" for backward compatibility)
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Set agent state to inactive
    agent_status_db[user_id] = "inactive"
    
    return {
        "success": True,
        "message": "Agent deactivated successfully",
        "status": "inactive",  # Legacy field
        "state": "inactive"  # New state field
    }

@router.get("/status")
def get_agent_status(authorization: str = Header(None)):
    """
    Get the current status of the AI agent for the authenticated user.
    (Legacy endpoint - kept for backward compatibility)
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Get agent status (default to inactive)
    status = agent_status_db.get(user_id, "inactive")
    helper_installed = helper_installed_db.get(user_id, False)
    
    return {
        "success": True,
        "message": "Agent status retrieved",
        "status": status,
        "helper_installed": helper_installed
    }

# ==================== PART 1: Agent State Synchronization ====================

class AgentStateUpdate(BaseModel):
    """Model for updating agent state"""
    state: str  # "inactive" | "waiting" | "active" | "paused"

@router.get("/state")
def get_agent_state(authorization: str = Header(None)):
    """
    Get the current agent state for the authenticated user.
    This is the single source of truth for agent state.
    
    States:
    - inactive: Agent is not active (default)
    - waiting: Agent is waiting for service request (extension visible)
    - active: Agent is actively executing a service request
    - paused: Agent execution is paused (waiting for user input)
    
    Also returns extension presence based on heartbeat.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Get agent state (default to inactive)
    state = agent_status_db.get(user_id, "inactive")
    
    # Check if extension is present (heartbeat within last 15 seconds)
    last_heartbeat = heartbeat_db.get(user_id)
    extension_present = False
    if last_heartbeat:
        time_since_heartbeat = (datetime.now() - last_heartbeat).total_seconds()
        extension_present = time_since_heartbeat < 15  # Consider present if heartbeat within 15 seconds
    
    return {
        "success": True,
        "message": "Agent state retrieved",
        "state": state,
        "extension_present": extension_present,
        "last_heartbeat": last_heartbeat.isoformat() if last_heartbeat else None
    }

@router.post("/state")
def update_agent_state(state_update: AgentStateUpdate, authorization: str = Header(None)):
    """
    Update the agent state for the authenticated user.
    This is the single source of truth for agent state.
    
    Valid states:
    - inactive: Agent is not active
    - waiting: Agent is waiting for service request
    - active: Agent is actively executing
    - paused: Agent execution is paused
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Validate state
    valid_states = ["inactive", "waiting", "active", "paused"]
    if state_update.state not in valid_states:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state. Must be one of: {', '.join(valid_states)}"
        )
    
    # Store previous state for logging
    previous_state = agent_status_db.get(user_id, "inactive")
    
    # Update state
    agent_status_db[user_id] = state_update.state
    
    # Log state change
    if user_id not in activity_db:
        activity_db[user_id] = []
    
    activity_db[user_id].append({
        "action": "state_changed",
        "description": f"Agent state changed from {previous_state} to {state_update.state}",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "message": "Agent state updated successfully",
        "state": state_update.state,
        "previous_state": previous_state
    }

@router.post("/heartbeat")
def agent_heartbeat(authorization: str = Header(None)):
    """
    Heartbeat endpoint - Optional (not required for standalone mode)
    Can be used for future client connections
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Update heartbeat timestamp
    heartbeat_db[user_id] = datetime.now()
    
    return {
        "success": True,
        "message": "Heartbeat received",
        "timestamp": heartbeat_db[user_id].isoformat()
    }

@router.post("/helper-connected")
def helper_connected(authorization: str = Header(None)):
    """
    Optional endpoint - Not required for standalone mode
    Can be used for future client integrations
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Mark helper as connected
    helper_installed_db[user_id] = True
    
    # Log the event
    if user_id not in activity_db:
        activity_db[user_id] = []
    
    activity_db[user_id].append({
        "action": "helper_connected",
        "description": "KYRON helper connected",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "message": "Helper marked as connected",
        "helper_installed": True
    }

@router.get("/activity")
def get_activity(authorization: str = Header(None)):
    """
    Get activity log for the authenticated user.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    if user_id not in activity_db:
        return {
            "success": True,
            "message": "Activity log retrieved",
            "activities": []
        }
    
    return {
        "success": True,
        "message": "Activity log retrieved",
        "activities": activity_db[user_id]
    }

@router.post("/activity")
def log_activity(activity: ActivityLog, authorization: str = Header(None)):
    """
    Log a new activity (called by Chrome extension or backend logic).
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Store activity
    if user_id not in activity_db:
        activity_db[user_id] = []
    
    activity_data = activity.dict()
    activity_data["timestamp"] = datetime.now().isoformat()
    activity_db[user_id].append(activity_data)
    
    return {
        "success": True,
        "message": "Activity logged successfully"
    }
