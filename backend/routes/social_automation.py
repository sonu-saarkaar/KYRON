"""
KYRON Social Automation & Live Mirror Routes.

Endpoints:
- GET  /api/kyron/social/state               -> Full mirror state, ONJ, steps feed & live stats
- POST /api/kyron/social/whatsapp/peek       -> Peek unread WhatsApp messages & vocal summary
- POST /api/kyron/social/whatsapp/reply      -> Send user-dictated WhatsApp reply
- POST /api/kyron/social/whatsapp/smart-reply-> Send autonomous smart reply using Sonu's memory
- POST /api/kyron/social/instagram/auto-reply-> Auto-reply to all Instagram DMs & vocal broadcast
- POST /api/kyron/social/mirror/switch       -> Toggle mirror mode (whatsapp / instagram / desktop)
- GET  /api/kyron/social/stats               -> Work summary stats (kitna kaam kia)
- GET  /api/kyron/social/task-history        -> Session-wise task history
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from services.social_automation_service import social_automation_service
from services.dograh_voice_engine import dograh_voice_engine

router = APIRouter(prefix="/api/kyron/social", tags=["social-automation-mirror"])


class ReplyRequest(BaseModel):
    contact: str = Field(..., description="Recipient contact name or phone number")
    message: str = Field(..., description="Message text to send")


class SmartReplyRequest(BaseModel):
    contact: Optional[str] = Field(None, description="Optional target contact filter")


class MirrorSwitchRequest(BaseModel):
    mode: str = Field(..., description="'whatsapp' | 'instagram' | 'desktop'")


@router.get("/state")
def get_mirror_state():
    """Returns complete real-time screen mirror, ONJ, steps feed, and social state."""
    return social_automation_service.get_mirror_state()


class SearchAndSendRequest(BaseModel):
    contact: str = Field(..., description="Contact name to search (e.g. 'Sonu')")
    message: str = Field(..., description="Message text to send (e.g. 'Hi Sonu')")


@router.post("/whatsapp/open")
def open_whatsapp():
    """Launches WhatsApp application and arms OBG desktop listener."""
    res = social_automation_service.open_whatsapp_app()
    if res.get("voice_vocalization"):
        dograh_voice_engine.speak_instant(res["voice_vocalization"])
    return res


@router.post("/whatsapp/search-and-send")
def search_and_send_whatsapp(req: SearchAndSendRequest):
    """Searches for contact in WhatsApp, types message, dispatches it, and speaks confirmation."""
    if not req.contact.strip() or not req.message.strip():
        raise HTTPException(status_code=400, detail="Contact and message cannot be empty.")
    res = social_automation_service.search_and_send_whatsapp(req.contact, req.message)
    if res.get("voice_vocalization"):
        dograh_voice_engine.speak_instant(res["voice_vocalization"])
    return res


@router.post("/whatsapp/peek")
def peek_whatsapp():
    """
    Peeks WhatsApp without opening individual chats.
    Reads messages from top previews and speaks out loud.
    """
    res = social_automation_service.peek_whatsapp()
    # Vocalize via Dograh native macOS speech
    if res.get("voice_vocalization"):
        dograh_voice_engine.speak_instant(res["voice_vocalization"])
    return res


@router.post("/whatsapp/reply")
def reply_whatsapp(req: ReplyRequest):
    """Sends user-specified reply to a contact."""
    if not req.contact.strip() or not req.message.strip():
        raise HTTPException(status_code=400, detail="Contact and message are required.")
    res = social_automation_service.reply_whatsapp_custom(req.contact, req.message)
    if res.get("voice_vocalization"):
        dograh_voice_engine.speak_instant(res["voice_vocalization"])
    return res


@router.post("/whatsapp/smart-reply")
def smart_reply_whatsapp(req: SmartReplyRequest):
    """
    Autonomous smart reply using Sonu's memory and master profile.
    """
    res = social_automation_service.smart_reply_from_memory(req.contact)
    if res.get("voice_vocalization"):
        dograh_voice_engine.speak_instant(res["voice_vocalization"])
    return res


@router.post("/instagram/auto-reply")
def auto_reply_instagram():
    """
    Iterates through Instagram DMs, replies to all senders sequentially,
    and vocalizes confirmations out loud in real-time.
    """
    res = social_automation_service.auto_reply_instagram()
    if res.get("voice_vocalization"):
        dograh_voice_engine.speak_instant(res["voice_vocalization"])
    return res


@router.post("/mirror/switch")
def switch_mirror(req: MirrorSwitchRequest):
    """Switches the live screen mirror viewport between Chrome apps."""
    mode = req.mode.lower()
    if mode not in ["whatsapp", "instagram", "desktop"]:
        raise HTTPException(status_code=400, detail="Invalid mode.")
    
    social_automation_service.mirror_mode = mode
    if mode == "whatsapp":
        social_automation_service.active_app = "Google Chrome (WhatsApp Web)"
        social_automation_service.current_url = "https://web.whatsapp.com"
    elif mode == "instagram":
        social_automation_service.active_app = "Google Chrome (Instagram Direct)"
        social_automation_service.current_url = "https://www.instagram.com/direct/inbox/"
    else:
        social_automation_service.active_app = "macOS Sequoia Desktop"
        social_automation_service.current_url = "localhost:3000/chat/kyron"
        
    return social_automation_service.get_mirror_state()


@router.get("/stats")
def get_work_stats():
    """Returns overview of work executed by Kyron."""
    return {
        "success": True,
        "work_stats": social_automation_service.work_stats
    }


@router.get("/task-history")
def get_task_history():
    """Returns session-wise task history."""
    return {
        "success": True,
        "task_history": social_automation_service.task_history
    }
