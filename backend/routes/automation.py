"""
KYRON Automation Routes
Handles Playwright automation and AI Vision integration
"""

from fastapi import APIRouter, HTTPException, Header, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import json

from auth_utils import verify_token
from services.playwright_automation import get_automation_engine, PlaywrightAutomationEngine
from services.ai_vision import create_ai_vision_service

router = APIRouter()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Automation session storage
automation_sessions: Dict[str, Dict] = {}

class AutomationRequest(BaseModel):
    """Request model for automation actions"""
    url: Optional[str] = None
    action: str  # "analyze", "fill", "navigate", "screenshot"
    field_mappings: Optional[List[Dict[str, Any]]] = None
    selectors: Optional[List[str]] = None

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time communication with Chrome extension
    """
    await websocket.accept()
    active_connections[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message.get("type") == "analyze_page":
                # Analyze current page using AI Vision
                session_id = message.get("session_id")
                if not session_id:
                    session_id = str(uuid.uuid4())
                
                engine = get_automation_engine()
                
                try:
                    await engine.initialize()
                    screenshot = await engine.capture_screenshot(session_id)
                    html, fields = await engine.get_page_html(session_id)
                    
                    # Use AI Vision to analyze
                    ai_service = create_ai_vision_service()
                    analysis = ai_service.analyze_screenshot(screenshot, html[:2000])
                    
                    await websocket.send_json({
                        "type": "analysis_complete",
                        "session_id": session_id,
                        "analysis": analysis,
                        "fields": fields
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif message.get("type") == "fill_form":
                # Fill form with mapped data
                session_id = message.get("session_id")
                field_mappings = message.get("field_mappings", [])
                
                engine = get_automation_engine()
                result = await engine.fill_form_batch(session_id, field_mappings)
                
                await websocket.send_json({
                    "type": "fill_complete",
                    "result": result
                })
            
    except WebSocketDisconnect:
        if user_id in active_connections:
            del active_connections[user_id]

@router.post("/session/create")
async def create_automation_session(
    url: Optional[str] = None,
    authorization: str = Header(None)
):
    """Create a new automation session"""
    user_id = verify_token(authorization)
    session_id = str(uuid.uuid4())
    
    engine = get_automation_engine()
    await engine.initialize()
    
    session_info = await engine.create_session(session_id, url)
    
    automation_sessions[session_id] = {
        "user_id": user_id,
        "session_info": session_info,
        "created_at": None  # Add timestamp
    }
    
    return {
        "success": True,
        "session_id": session_id,
        "session_info": session_info
    }

@router.post("/session/{session_id}/navigate")
async def navigate_session(
    session_id: str,
    url: str,
    authorization: str = Header(None)
):
    """Navigate to a URL in an automation session"""
    user_id = verify_token(authorization)
    
    # Verify session belongs to user
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if automation_sessions[session_id]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    engine = get_automation_engine()
    result = await engine.navigate(session_id, url)
    
    return {
        "success": True,
        "result": result
    }

@router.post("/session/{session_id}/analyze")
async def analyze_page(
    session_id: str,
    authorization: str = Header(None)
):
    """Analyze current page using AI Vision"""
    user_id = verify_token(authorization)
    
    # Verify session
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = get_automation_engine()
    
    # Capture screenshot and HTML
    screenshot = await engine.capture_screenshot(session_id, full_page=True)
    html, fields = await engine.get_page_html(session_id)
    
    # Analyze with AI Vision
    try:
        ai_service = create_ai_vision_service()
        analysis = ai_service.analyze_screenshot(screenshot, html[:2000])
    except Exception as e:
        # If AI service fails, return basic analysis
        analysis = {
            "success": False,
            "error": f"AI Vision service unavailable: {str(e)}",
            "fields": fields
        }
    
    return {
        "success": True,
        "session_id": session_id,
        "analysis": analysis,
        "fields": fields
    }

@router.post("/session/{session_id}/fill")
async def fill_form(
    session_id: str,
    field_mappings: List[Dict[str, Any]],
    authorization: str = Header(None)
):
    """Fill form fields based on AI analysis"""
    user_id = verify_token(authorization)
    
    # Verify session
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = get_automation_engine()
    result = await engine.fill_form_batch(session_id, field_mappings)
    
    return {
        "success": True,
        "result": result
    }

@router.get("/session/{session_id}/screenshot")
async def get_screenshot(
    session_id: str,
    authorization: str = Header(None)
):
    """Get screenshot of current page (safe: never hard-crashes)."""
    user_id = verify_token(authorization)

    # Verify session
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        engine = get_automation_engine()
        screenshot = await engine.capture_screenshot(session_id, full_page=True)
        return {
            "success": True,
            "screenshot": screenshot,
            "format": "base64"
        }
    except Exception as e:
        # Log and return graceful fallback instead of 500
        logging.getLogger(__name__).warning(f"Screenshot capture failed for {session_id}: {e}")
        raise HTTPException(
            status_code=503,
            detail="Unable to capture screenshot right now, but automation is still running."
        )

@router.delete("/session/{session_id}")
async def close_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Close an automation session"""
    user_id = verify_token(authorization)
    
    # Verify session
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if automation_sessions[session_id]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    engine = get_automation_engine()
    await engine.close_session(session_id)
    
    del automation_sessions[session_id]
    
    return {
        "success": True,
        "message": "Session closed"
    }

