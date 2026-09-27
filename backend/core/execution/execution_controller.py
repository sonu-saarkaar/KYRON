"""
KYRON Execution Engine - ExecutionController

Controls lifecycle: start / pause / resume / stop
Syncs with UI popup
Preserves and restores state
"""

from typing import Dict, Optional, Any
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """Execution status"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_USER = "waiting_user"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"

class ExecutionController:
    """
    Controls execution lifecycle and state synchronization
    """
    
    def __init__(self, session_id: str, memory_layer, popup_sync_manager):
        self.session_id = session_id
        self.memory_layer = memory_layer
        self.popup_sync_manager = popup_sync_manager
        self.status = ExecutionStatus.IDLE
        self.current_step_id = ""
        self.current_action = ""
        self.progress = {"step": 0, "total": 0, "action": ""}
        self._pause_event = asyncio.Event()
        self._resume_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._pause_event.set()  # Initially paused
    
    async def start(self):
        """Start execution"""
        if self.status == ExecutionStatus.RUNNING:
            logger.warning("Execution already running")
            return
        
        self.status = ExecutionStatus.INITIALIZING
        await self._update_popup("Initializing KYRON...", ExecutionStatus.INITIALIZING)
        
        # Clear stop event
        self._stop_event.clear()
        self._resume_event.set()
        self._pause_event.clear()
        
        self.status = ExecutionStatus.RUNNING
        logger.info(f"Execution started for session {self.session_id}")
    
    async def pause(self, reason: str = "User requested pause"):
        """Pause execution"""
        if self.status != ExecutionStatus.RUNNING:
            logger.warning(f"Cannot pause: status is {self.status.value}")
            return
        
        self.status = ExecutionStatus.PAUSED
        self._pause_event.set()
        self._resume_event.clear()
        
        await self._update_popup(f"Paused: {reason}", ExecutionStatus.PAUSED)
        logger.info(f"Execution paused: {reason}")
    
    async def resume(self):
        """Resume execution"""
        if self.status != ExecutionStatus.PAUSED:
            logger.warning(f"Cannot resume: status is {self.status.value}")
            return
        
        self.status = ExecutionStatus.RUNNING
        self._pause_event.clear()
        self._resume_event.set()
        
        await self._update_popup("Resuming execution...", ExecutionStatus.RUNNING)
        logger.info("Execution resumed")
    
    async def stop(self, reason: str = "User requested stop"):
        """Stop execution"""
        self.status = ExecutionStatus.STOPPED
        self._stop_event.set()
        self._pause_event.set()
        self._resume_event.clear()
        
        await self._update_popup(f"Stopped: {reason}", ExecutionStatus.STOPPED)
        logger.info(f"Execution stopped: {reason}")
    
    async def wait_if_paused(self):
        """Wait if execution is paused"""
        if self.status == ExecutionStatus.PAUSED:
            await self._pause_event.wait()
    
    def is_stopped(self) -> bool:
        """Check if execution is stopped"""
        return self.status == ExecutionStatus.STOPPED or self._stop_event.is_set()
    
    def is_paused(self) -> bool:
        """Check if execution is paused"""
        return self.status == ExecutionStatus.PAUSED
    
    async def update_progress(self, step: int, total: int, action: str, step_id: str = ""):
        """Update execution progress"""
        self.progress = {"step": step, "total": total, "action": action}
        self.current_step_id = step_id
        self.current_action = action
        
        progress_text = f"Step {step}/{total}: {action}"
        await self._update_popup(progress_text, self.status, progress_text)
        logger.debug(f"Progress: {progress_text}")
    
    async def wait_for_user(self, message: str, field_name: str = ""):
        """Wait for user input"""
        self.status = ExecutionStatus.WAITING_USER
        await self._update_popup(f"Waiting: {message}", ExecutionStatus.WAITING_USER, message)
        logger.info(f"Waiting for user: {message}")
    
    async def complete(self, message: str = "Execution completed"):
        """Mark execution as complete"""
        self.status = ExecutionStatus.COMPLETED
        await self._update_popup(message, ExecutionStatus.COMPLETED)
        logger.info(message)
    
    async def error(self, error_message: str):
        """Mark execution as error"""
        self.status = ExecutionStatus.ERROR
        await self._update_popup(f"Error: {error_message}", ExecutionStatus.ERROR)
        logger.error(error_message)
    
    async def _update_popup(self, message: str, status: ExecutionStatus, progress: str = ""):
        """Update popup UI"""
        if self.popup_sync_manager:
            await self.popup_sync_manager.update_status(
                status.value,
                message,
                progress or self.current_action
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        return {
            "status": self.status.value,
            "current_step_id": self.current_step_id,
            "current_action": self.current_action,
            "progress": self.progress
        }

