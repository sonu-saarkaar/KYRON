"""
Service Request Management
Handles creation, storage, and retrieval of service requests.
Each request contains selected options and execution status.
"""

from fastapi import APIRouter, HTTPException, Header, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from auth_utils import verify_token
from services_catalog import get_service_definition, ServiceType

# Create router for service request endpoints
router = APIRouter()

# Temporary in-memory storage (replace with database later)
# Format: {request_id: {user_id, service_id, selected_options, form_data, status, created_at, updated_at}}
service_requests_db = {}

# Request statuses (using string constants)
REQUEST_STATUS = {
    "DRAFT": "draft",  # Request created but not started
    "PENDING": "pending",  # Waiting to be executed
    "IN_PROGRESS": "in_progress",  # Currently being executed
    "PAUSED": "paused",  # Execution paused (e.g., waiting for OTP)
    "COMPLETED": "completed",  # Successfully completed
    "FAILED": "failed",  # Execution failed
    "CANCELLED": "cancelled"  # User cancelled
}

class ServiceRequestCreate(BaseModel):
    """Model for creating a service request"""
    service_id: str  # e.g., "pan_card"
    selected_options: Dict[str, str]  # {step_id: selected_option_value}
    
class ServiceRequestUpdate(BaseModel):
    """Model for updating a service request"""
    status: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None  # Derived form data for filling
    acknowledgement_number: Optional[str] = None
    snapshot_url: Optional[str] = None
    error_message: Optional[str] = None

class ServiceRequestResponse(BaseModel):
    """Response model for service request"""
    id: str
    user_id: str
    service_id: str
    service_name: str
    selected_options: Dict[str, str]
    form_data: Dict[str, Any]
    status: str
    acknowledgement_number: Optional[str]
    snapshot_url: Optional[str]
    created_at: str
    updated_at: str

@router.get("/catalog")
def get_service_catalog_endpoint():
    """
    Get the complete service catalog.
    Returns all available services with their steps and options.
    """
    from services_catalog import get_all_services
    return {
        "success": True,
        "message": "Service catalog retrieved",
        "services": get_all_services()
    }

@router.post("/request")
def create_service_request(request: ServiceRequestCreate, authorization: str = Header(None)):
    """
    Create a new service request.
    
    The request contains:
    - service_id: The type of service (e.g., "pan_card")
    - selected_options: Dictionary mapping step_id to selected option value
    
    Returns the created request with generated ID and derived form data.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Validate service exists
    service_def = get_service_definition(request.service_id)
    if not service_def:
        raise HTTPException(status_code=404, detail=f"Service '{request.service_id}' not found")
    
    # Validate selected options match service steps
    valid_step_ids = {step.id for step in service_def.steps}
    provided_step_ids = set(request.selected_options.keys())
    
    # Check all required steps are provided
    required_steps = {step.id for step in service_def.steps if step.required}
    missing_required = required_steps - provided_step_ids
    if missing_required:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required options for steps: {', '.join(missing_required)}"
        )
    
    # Check no invalid steps
    invalid_steps = provided_step_ids - valid_step_ids
    if invalid_steps:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step IDs: {', '.join(invalid_steps)}"
        )
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Derive form data from selected options
    form_data = {}
    for step in service_def.steps:
        if step.id in request.selected_options:
            selected_value = request.selected_options[step.id]
            # Use field_mapping if available
            if step.field_mapping and selected_value in step.field_mapping:
                form_data.update(step.field_mapping[selected_value])
            else:
                # Default mapping: use step_id as key, selected_value as value
                form_data[step.id] = selected_value
    
    # Create request record
    now = datetime.now()
    service_requests_db[request_id] = {
        "id": request_id,
        "user_id": user_id,
        "service_id": request.service_id,
        "service_name": service_def.name,
        "selected_options": request.selected_options,
        "form_data": form_data,
        "status": REQUEST_STATUS["DRAFT"],
        "acknowledgement_number": None,
        "snapshot_url": None,
        "error_message": None,
        "created_at": now,
        "updated_at": now
    }
    
    return {
        "success": True,
        "message": "Service request created successfully",
        "request": {
            "id": request_id,
            "service_id": request.service_id,
            "service_name": service_def.name,
            "status": REQUEST_STATUS["DRAFT"],
            "selected_options": request.selected_options,
            "form_data": form_data,
            "created_at": now.isoformat()
        }
    }

@router.get("/requests")
def get_service_requests(authorization: str = Header(None)):
    """
    Get all service requests for the authenticated user.
    Returns list of requests sorted by creation date (newest first).
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Filter requests for this user
    user_requests = [
        request for request in service_requests_db.values()
        if request["user_id"] == user_id
    ]
    
    # Sort by created_at (newest first)
    user_requests.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Serialize for response
    requests_data = [
        {
            "id": req["id"],
            "service_id": req["service_id"],
            "service_name": req["service_name"],
            "status": req["status"],
            "acknowledgement_number": req["acknowledgement_number"],
            "created_at": req["created_at"].isoformat(),
            "updated_at": req["updated_at"].isoformat()
        }
        for req in user_requests
    ]
    
    return {
        "success": True,
        "message": "Service requests retrieved",
        "requests": requests_data,
        "count": len(requests_data)
    }

@router.get("/request/{request_id}")
def get_service_request(request_id: str, authorization: str = Header(None)):
    """
    Get a specific service request by ID.
    Only returns requests belonging to the authenticated user.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Find request
    if request_id not in service_requests_db:
        raise HTTPException(status_code=404, detail="Service request not found")
    
    request = service_requests_db[request_id]
    
    # Check ownership
    if request["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Serialize for response
    return {
        "success": True,
        "message": "Service request retrieved",
        "request": {
            "id": request["id"],
            "user_id": request["user_id"],
            "service_id": request["service_id"],
            "service_name": request["service_name"],
            "selected_options": request["selected_options"],
            "form_data": request["form_data"],
            "status": request["status"],
            "acknowledgement_number": request["acknowledgement_number"],
            "snapshot_url": request["snapshot_url"],
            "error_message": request["error_message"],
            "created_at": request["created_at"].isoformat(),
            "updated_at": request["updated_at"].isoformat()
        }
    }

@router.get("/request/active")
def get_active_service_request(authorization: str = Header(None)):
    """
    Get the currently active service request for the user.
    Active means status is "pending" or "in_progress" or "paused".
    Returns None if no active request exists.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Find active request
    active_statuses = [REQUEST_STATUS["PENDING"], REQUEST_STATUS["IN_PROGRESS"], REQUEST_STATUS["PAUSED"]]
    active_request = None
    
    for request in service_requests_db.values():
        if request["user_id"] == user_id and request["status"] in active_statuses:
            active_request = request
            break
    
    if not active_request:
        return {
            "success": True,
            "message": "No active service request",
            "request": None
        }
    
    # Serialize for response
    return {
        "success": True,
        "message": "Active service request retrieved",
        "request": {
            "id": active_request["id"],
            "service_id": active_request["service_id"],
            "service_name": active_request["service_name"],
            "selected_options": active_request["selected_options"],
            "form_data": active_request["form_data"],
            "status": active_request["status"],
            "created_at": active_request["created_at"].isoformat(),
            "updated_at": active_request["updated_at"].isoformat()
        }
    }

@router.post("/request/{request_id}/acknowledgement")
def save_acknowledgement(
    request_id: str,
    acknowledgement_data: Dict[str, Any] = Body(...),
    authorization: str = Header(None)
):
    """
    PART 4: Save acknowledgement number and snapshot URL after form submission.
    This endpoint is called by the extension when it detects form submission.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Find request
    if request_id not in service_requests_db:
        raise HTTPException(status_code=404, detail="Service request not found")
    
    request = service_requests_db[request_id]
    
    # Check ownership
    if request["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update acknowledgement fields
    if "acknowledgement_number" in acknowledgement_data:
        request["acknowledgement_number"] = acknowledgement_data["acknowledgement_number"]
    
    if "snapshot_url" in acknowledgement_data:
        request["snapshot_url"] = acknowledgement_data["snapshot_url"]
    
    # Update status to completed if acknowledgement is provided
    if acknowledgement_data.get("acknowledgement_number"):
        request["status"] = REQUEST_STATUS["COMPLETED"]
    
    # Update timestamp
    request["updated_at"] = datetime.now()
    
    return {
        "success": True,
        "message": "Acknowledgement saved successfully",
        "request": {
            "id": request["id"],
            "acknowledgement_number": request["acknowledgement_number"],
            "snapshot_url": request["snapshot_url"],
            "status": request["status"],
            "updated_at": request["updated_at"].isoformat()
        }
    }

@router.put("/request/{request_id}")
def update_service_request(
    request_id: str,
    update: ServiceRequestUpdate,
    authorization: str = Header(None)
):
    """
    Update a service request.
    Can update status, form_data, acknowledgement_number, snapshot_url, error_message.
    Only the owner can update their request.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Find request
    if request_id not in service_requests_db:
        raise HTTPException(status_code=404, detail="Service request not found")
    
    request = service_requests_db[request_id]
    
    # Check ownership
    if request["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if update.status:
        # Validate status
        valid_statuses = list(REQUEST_STATUS.values())
        if update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status: {update.status}")
        request["status"] = update.status
    
    if update.form_data is not None:
        request["form_data"].update(update.form_data)
    
    if update.acknowledgement_number is not None:
        request["acknowledgement_number"] = update.acknowledgement_number
    
    if update.snapshot_url is not None:
        request["snapshot_url"] = update.snapshot_url
    
    if update.error_message is not None:
        request["error_message"] = update.error_message
    
    # Update timestamp
    request["updated_at"] = datetime.now()
    
    return {
        "success": True,
        "message": "Service request updated successfully",
        "request": {
            "id": request["id"],
            "status": request["status"],
            "updated_at": request["updated_at"].isoformat()
        }
    }

