"""
KYRON Screen Sharing Routes
API endpoints for screen sharing and mode switching
"""

from fastapi import APIRouter, HTTPException, Header, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import json

from auth_utils import verify_token
from services.screen_share import get_screen_share_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class CreateSessionRequest(BaseModel):
    """Request to create screen sharing session"""
    mode: str = "automatic"  # "manual" or "automatic"

class SetModeRequest(BaseModel):
    """Request to change mode"""
    mode: str  # "manual" or "automatic"

@router.post("/session/create")
def create_session(
    request: CreateSessionRequest,
    authorization: str = Header(None)
):
    """Create a screen sharing session"""
    user_id = verify_token(authorization)
    import uuid
    session_id = str(uuid.uuid4())
    
    screen_share_service = get_screen_share_service()
    result = screen_share_service.create_session(session_id, user_id, request.mode)
    
    return {
        "success": True,
        "session": result
    }

@router.post("/session/{session_id}/mode")
def set_mode(
    session_id: str,
    request: SetModeRequest,
    authorization: str = Header(None)
):
    """Change session mode (manual/automatic)"""
    user_id = verify_token(authorization)
    
    screen_share_service = get_screen_share_service()
    session = screen_share_service.get_session(session_id)
    
    if not session or session["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = screen_share_service.set_mode(session_id, request.mode)
    
    return result

class ScreenshotRequest(BaseModel):
    """Request to add screenshot"""
    screenshot: str  # Base64 encoded

@router.post("/session/{session_id}/screenshot")
def add_screenshot(
    session_id: str,
    request: ScreenshotRequest,
    authorization: str = Header(None)
):
    """Add screenshot to session"""
    user_id = verify_token(authorization)
    
    screen_share_service = get_screen_share_service()
    session = screen_share_service.get_session(session_id)
    
    if not session or session["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = screen_share_service.add_screenshot(session_id, request.screenshot)
    
    return result

@router.get("/session/{session_id}")
def get_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Get session information"""
    user_id = verify_token(authorization)
    
    screen_share_service = get_screen_share_service()
    session = screen_share_service.get_session(session_id)
    
    if not session or session["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "session": session
    }

@router.delete("/session/{session_id}")
def close_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Close screen sharing session"""
    user_id = verify_token(authorization)
    
    screen_share_service = get_screen_share_service()
    session = screen_share_service.get_session(session_id)
    
    if not session or session["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = screen_share_service.close_session(session_id)
    
    return result

@router.websocket("/ws/{session_id}")
async def websocket_screen_share(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time screen sharing"""
    await websocket.accept()
    
    screen_share_service = get_screen_share_service()
    session = screen_share_service.get_session(session_id)
    
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "screenshot":
                # Receive screenshot
                screenshot = message.get("screenshot")
                screen_share_service.add_screenshot(session_id, screenshot)
                await websocket.send_json({
                    "type": "screenshot_received",
                    "success": True
                })
            
            elif message.get("type") == "mode_change":
                # Change mode
                mode = message.get("mode")
                result = screen_share_service.set_mode(session_id, mode)
                await websocket.send_json({
                    "type": "mode_changed",
                    "result": result
                })
            
            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        logger.info(f"Screen share WebSocket disconnected: {session_id}")

