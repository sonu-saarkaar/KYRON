"""
KYRON Intelligence - Multi-Tab Manager

Manages multiple browser tabs
Detects new tabs automatically
Switches context without losing state
Maintains smooth transitions
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class TabStatus(Enum):
    """Tab status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    NEW = "new"

@dataclass
class TabContext:
    """Tab context information"""
    tab_id: str
    page_url: str
    page_title: str
    status: TabStatus = TabStatus.NEW
    created_at: float = 0.0
    last_activity: float = 0.0
    is_main_tab: bool = False
    session_id: str = ""

class MultiTabManager:
    """
    Manages multiple browser tabs with context switching
    """
    
    def __init__(self):
        self.tabs: Dict[str, TabContext] = {}  # tab_id -> TabContext
        self.active_tab_id: Optional[str] = None
        self.main_tab_id: Optional[str] = None
    
    async def detect_new_tabs(
        self,
        browser_context,
        session_id: str,
        main_page
    ) -> List[Any]:
        """
        Detect new tabs that opened
        
        Returns:
            List of new page objects
        """
        try:
            # Get all pages in context
            all_pages = browser_context.pages
            
            new_pages = []
            
            for page in all_pages:
                try:
                    page_url = page.url
                    if not page_url or page_url == "about:blank":
                        continue
                    
                    # Check if this is a new tab
                    tab_id = self._get_tab_id(page)
                    
                    if tab_id not in self.tabs:
                        # New tab detected
                        tab_context = TabContext(
                            tab_id=tab_id,
                            page_url=page_url,
                            page_title=await page.title() or "",
                            status=TabStatus.NEW,
                            created_at=asyncio.get_event_loop().time(),
                            last_activity=asyncio.get_event_loop().time(),
                            session_id=session_id
                        )
                        
                        self.tabs[tab_id] = tab_context
                        new_pages.append(page)
                        
                        logger.info(f"New tab detected: {tab_id} - {page_url}")
                except Exception as e:
                    logger.debug(f"Error checking page: {e}")
                    continue
            
            return new_pages
            
        except Exception as e:
            logger.error(f"Error detecting new tabs: {e}")
            return []
    
    def _get_tab_id(self, page) -> str:
        """Generate unique tab ID"""
        try:
            # Use URL and title as identifier
            url = page.url
            # Create hash-like ID
            import hashlib
            tab_id = hashlib.md5(url.encode()).hexdigest()[:8]
            return tab_id
        except:
            return f"tab_{id(page)}"
    
    async def switch_to_tab(
        self,
        tab_id: str,
        browser_context
    ) -> Optional[Any]:
        """
        Switch to a specific tab
        
        Returns:
            Page object for the tab
        """
        try:
            all_pages = browser_context.pages
            
            for page in all_pages:
                current_tab_id = self._get_tab_id(page)
                if current_tab_id == tab_id:
                    # Update tab context
                    if tab_id in self.tabs:
                        self.tabs[tab_id].status = TabStatus.ACTIVE
                        self.tabs[tab_id].last_activity = asyncio.get_event_loop().time()
                    
                    # Mark other tabs as inactive
                    for other_tab_id, other_context in self.tabs.items():
                        if other_tab_id != tab_id:
                            if other_context.status == TabStatus.ACTIVE:
                                other_context.status = TabStatus.INACTIVE
                    
                    self.active_tab_id = tab_id
                    
                    # Bring page to front
                    await page.bring_to_front()
                    
                    logger.info(f"Switched to tab: {tab_id}")
                    return page
            
            return None
            
        except Exception as e:
            logger.error(f"Error switching to tab: {e}")
            return None
    
    async def switch_to_new_tab(
        self,
        browser_context,
        session_id: str
    ) -> Optional[Any]:
        """
        Switch to the most recently opened new tab
        
        Returns:
            Page object for the new tab
        """
        try:
            # Find newest tab
            newest_tab = None
            newest_time = 0.0
            
            for tab_id, context in self.tabs.items():
                if context.status == TabStatus.NEW and context.created_at > newest_time:
                    newest_time = context.created_at
                    newest_tab = tab_id
            
            if newest_tab:
                return await self.switch_to_tab(newest_tab, browser_context)
            
            # If no new tab found, detect new tabs
            new_pages = await self.detect_new_tabs(browser_context, session_id, None)
            if new_pages:
                new_page = new_pages[0]
                new_tab_id = self._get_tab_id(new_page)
                return await self.switch_to_tab(new_tab_id, browser_context)
            
            return None
            
        except Exception as e:
            logger.error(f"Error switching to new tab: {e}")
            return None
    
    async def handle_popup_tab(
        self,
        browser_context,
        session_id: str,
        execution_state: Any
    ) -> Optional[Any]:
        """
        Handle popup/new tab that opened (e.g., after clicking Apply button)
        
        Returns:
            Page object for the new tab
        """
        try:
            # Wait a bit for tab to open
            await asyncio.sleep(1)
            
            # Detect new tabs
            new_pages = await self.detect_new_tabs(browser_context, session_id, None)
            
            if not new_pages:
                logger.warning("No new tabs detected after popup trigger")
                return None
            
            # Switch to the new tab
            new_page = new_pages[0]
            new_tab_id = self._get_tab_id(new_page)
            
            # Update execution state
            if execution_state:
                execution_state.active_tab_id = new_tab_id
            
            # Switch to new tab
            active_page = await self.switch_to_tab(new_tab_id, browser_context)
            
            if active_page:
                # Ensure full screen and 100% zoom
                await active_page.set_viewport_size({"width": 1920, "height": 1080})
                await active_page.evaluate("document.body.style.zoom = '1.0';")
                
                logger.info(f"Switched to popup tab: {new_tab_id} - {active_page.url}")
                return active_page
            
            return None
            
        except Exception as e:
            logger.error(f"Error handling popup tab: {e}")
            return None
    
    def get_active_tab(self) -> Optional[TabContext]:
        """Get active tab context"""
        if self.active_tab_id:
            return self.tabs.get(self.active_tab_id)
        return None
    
    def get_all_tabs(self) -> List[TabContext]:
        """Get all tab contexts"""
        return list(self.tabs.values())
    
    def close_tab(self, tab_id: str):
        """Mark tab as closed"""
        if tab_id in self.tabs:
            self.tabs[tab_id].status = TabStatus.CLOSED
            if self.active_tab_id == tab_id:
                self.active_tab_id = None

