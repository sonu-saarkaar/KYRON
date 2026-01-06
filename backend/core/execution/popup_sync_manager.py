"""
KYRON Execution Engine - PopupSyncManager

Injects floating KYRON control panel
Shows live status and progress
Provides Start / Pause / Resume / Stop controls
"""

from typing import Optional, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class PopupSyncManager:
    """
    Manages floating control UI synchronization
    """
    
    def __init__(self):
        self.active_pages: Dict[str, Any] = {}  # session_id -> page
        self.control_script = self._get_control_script()
    
    def _get_control_script(self) -> str:
        """Get control UI injection script"""
        from services.kyron_control_ui import get_control_ui_script
        return get_control_ui_script()
    
    async def inject_control_ui(self, page, session_id: str):
        """Inject control UI into page"""
        try:
            # Inject control script
            await page.evaluate(self.control_script)
            
            # Store page reference
            self.active_pages[session_id] = page
            
            logger.info(f"Control UI injected for session {session_id}")
        except Exception as e:
            logger.error(f"Error injecting control UI: {e}")
    
    async def update_status(
        self,
        status: str,
        message: str,
        current_step: str = ""
    ):
        """Update control UI status"""
        try:
            # Update all active pages
            for session_id, page in self.active_pages.items():
                try:
                    await page.evaluate(f"""
                        if (window.updateKyronStatus) {{
                            window.updateKyronStatus(
                                '{status}',
                                '{message}',
                                '{current_step}',
                                '{current_step}'
                            );
                        }}
                    """)
                except Exception as e:
                    logger.debug(f"Error updating status on page {session_id}: {e}")
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    async def remove_control_ui(self, session_id: str):
        """Remove control UI from page"""
        try:
            page = self.active_pages.get(session_id)
            if page:
                await page.evaluate("""
                    const panel = document.getElementById('kyron-control-panel');
                    if (panel) {
                        panel.remove();
                    }
                """)
                del self.active_pages[session_id]
                logger.info(f"Control UI removed for session {session_id}")
        except Exception as e:
            logger.error(f"Error removing control UI: {e}")

