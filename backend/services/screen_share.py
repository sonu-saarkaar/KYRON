"""
KYRON Screen Sharing Service
Handles screen sharing and manual/automatic mode switching
"""

import asyncio
from typing import Dict, Optional, Callable
import logging
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class ScreenShareService:
    """Service for screen sharing capabilities"""
    
    def __init__(self):
        """Initialize screen sharing service"""
        self.active_sessions: Dict[str, Dict] = {}
        self.mode_callbacks: Dict[str, Callable] = {}
    
    def create_session(self, session_id: str, user_id: str, mode: str = "automatic") -> Dict:
        """
        Create a screen sharing session
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            mode: "manual" or "automatic"
            
        Returns:
            Session information
        """
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "mode": mode,
            "created_at": datetime.now(),
            "status": "active",
            "screenshots": []
        }
        
        logger.info(f"Screen share session created: {session_id} (mode: {mode})")
        
        return {
            "success": True,
            "session_id": session_id,
            "mode": mode,
            "status": "active"
        }
    
    def set_mode(self, session_id: str, mode: str) -> Dict:
        """
        Switch between manual and automatic modes
        
        Args:
            session_id: Session identifier
            mode: "manual" or "automatic"
            
        Returns:
            Mode change result
        """
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        if mode not in ["manual", "automatic"]:
            return {
                "success": False,
                "error": "Invalid mode. Must be 'manual' or 'automatic'"
            }
        
        old_mode = self.active_sessions[session_id]["mode"]
        self.active_sessions[session_id]["mode"] = mode
        
        # Trigger callback if registered
        if session_id in self.mode_callbacks:
            try:
                self.mode_callbacks[session_id](mode)
            except Exception as e:
                logger.error(f"Error in mode callback: {e}")
        
        logger.info(f"Session {session_id} mode changed: {old_mode} -> {mode}")
        
        return {
            "success": True,
            "session_id": session_id,
            "old_mode": old_mode,
            "new_mode": mode
        }
    
    def add_screenshot(self, session_id: str, screenshot_base64: str) -> Dict:
        """
        Add screenshot to session
        
        Args:
            session_id: Session identifier
            screenshot_base64: Base64 encoded screenshot
            
        Returns:
            Add result
        """
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        screenshot_data = {
            "data": screenshot_base64,
            "timestamp": datetime.now().isoformat()
        }
        
        self.active_sessions[session_id]["screenshots"].append(screenshot_data)
        
        # Keep only last 10 screenshots
        if len(self.active_sessions[session_id]["screenshots"]) > 10:
            self.active_sessions[session_id]["screenshots"] = \
                self.active_sessions[session_id]["screenshots"][-10:]
        
        return {
            "success": True,
            "screenshot_count": len(self.active_sessions[session_id]["screenshots"])
        }
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        return self.active_sessions.get(session_id)
    
    def register_mode_callback(self, session_id: str, callback: Callable):
        """Register callback for mode changes"""
        self.mode_callbacks[session_id] = callback
    
    def close_session(self, session_id: str) -> Dict:
        """Close screen sharing session"""
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        del self.active_sessions[session_id]
        
        if session_id in self.mode_callbacks:
            del self.mode_callbacks[session_id]
        
        logger.info(f"Screen share session closed: {session_id}")
        
        return {
            "success": True,
            "message": "Session closed"
        }


# Global instance
_screen_share_service: Optional[ScreenShareService] = None

def get_screen_share_service() -> ScreenShareService:
    """Get or create global screen share service instance"""
    global _screen_share_service
    if _screen_share_service is None:
        _screen_share_service = ScreenShareService()
    return _screen_share_service

