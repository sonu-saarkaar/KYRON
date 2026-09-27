"""
KYRON Voice Guidance Routes
API endpoints for voice commands and guidance
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional

from auth_utils import verify_token
from services.voice_service import get_voice_service

router = APIRouter()

class SpeakRequest(BaseModel):
    """Request to speak text"""
    text: str
    language: str = "en"

class GuideRequest(BaseModel):
    """Request for voice guidance"""
    steps: List[str]

@router.post("/speak")
def speak_text(
    request: SpeakRequest,
    authorization: str = Header(None)
):
    """Convert text to speech"""
    verify_token(authorization)
    
    voice_service = get_voice_service()
    result = voice_service.speak(request.text, request.language)
    
    if not result.get("success"):
        raise HTTPException(status_code=503, detail=result.get("error", "Voice service unavailable"))
    
    return {
        "success": True,
        "message": "Text spoken successfully"
    }

@router.post("/listen")
def listen_speech(
    timeout: int = 5,
    authorization: str = Header(None)
):
    """Listen for speech and convert to text"""
    verify_token(authorization)
    
    voice_service = get_voice_service()
    result = voice_service.listen(timeout)
    
    if not result.get("success"):
        raise HTTPException(status_code=503, detail=result.get("error", "Speech recognition unavailable"))
    
    return {
        "success": True,
        "text": result.get("text"),
        "confidence": result.get("confidence", 1.0)
    }

@router.post("/guide")
def guide_user(
    request: GuideRequest,
    authorization: str = Header(None)
):
    """Guide user through steps with voice"""
    verify_token(authorization)
    
    voice_service = get_voice_service()
    result = voice_service.guide_user(request.steps)
    
    return {
        "success": True,
        "guidance": result
    }

@router.get("/status")
def get_voice_status(authorization: str = Header(None)):
    """Get voice service status"""
    verify_token(authorization)
    
    voice_service = get_voice_service()
    
    return {
        "success": True,
        "tts_available": voice_service.tts_available,
        "stt_available": voice_service.stt_available
    }

