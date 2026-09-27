import asyncio
import subprocess
import logging
from typing import Dict, Any, List
import uuid
import time

logger = logging.getLogger(__name__)

class ApprovalQueueManager:
    """
    Unified central queue for all KYRON agent actions that require physical operator confirmation.
    Handles CodeAgent (apply diff), BrowserControl (submit/pay), and SystemControl (send/delete).
    """
    def __init__(self):
        self.pending_actions: Dict[str, Dict[str, Any]] = {}
        self.events: Dict[str, asyncio.Event] = {}
        self.resolutions: Dict[str, str] = {}
        self.listeners: List[Any] = []

    def _show_windows_toast(self, title: str, message: str, action_id: str):
        """Trigger a native Windows toast notification so user knows even if UI is closed (e.g. Cron tasks)."""
        try:
            # Escape single quotes
            message = message.replace("'", "")
            title = title.replace("'", "")
            ps_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $template = "<toast activationType='protocol' launch='http://localhost:3000/?action_id={action_id}'><visual><binding template='ToastText02'><text id='1'>{title}</text><text id='2'>{message}</text></binding></visual></toast>"
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("KYRON AGI").Show($toast)
            """
            subprocess.Popen(["powershell", "-Command", ps_script], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            logger.error(f"Failed to show toast notification: {e}")

    def register_pending_action(self, agent_type: str, description: str, payload: Dict[str, Any], risk_level: str = "high") -> str:
        """
        Registers a new paused action in the unified queue and notifies the user.
        """
        action_id = f"kyron-act-{uuid.uuid4().hex[:8]}"
        action = {
            "action_id": action_id,
            "agent_type": agent_type,  # CODE, BROWSER, SYSTEM
            "description": description,
            "payload": payload,
            "risk_level": risk_level,
            "status": "pending_confirmation",
            "created_at": time.time()
        }
        self.pending_actions[action_id] = action
        self.events[action_id] = asyncio.Event()
        logger.info(f"Registered pending {agent_type} action: {action_id}")
        
        # OS Notification for off-UI awareness (especially cron jobs)
        self._show_windows_toast("KYRON: Action Pending Approval", f"{agent_type} requires approval: {description[:50]}...", action_id)
        
        return action_id

    def get_all_pending(self) -> List[Dict[str, Any]]:
        """Returns all pending actions sorted by oldest first."""
        actions = list(self.pending_actions.values())
        actions.sort(key=lambda x: x["created_at"])
        return actions
        
    def get_action(self, action_id: str) -> Dict[str, Any]:
        return self.pending_actions.get(action_id)

    def resolve_action(self, action_id: str, resolution: str) -> Dict[str, Any]:
        """Marks an action as executed or rejected and removes from pending queue."""
        self.resolutions[action_id] = resolution
        if action_id in self.events:
            self.events[action_id].set()
            
        if action_id in self.pending_actions:
            action = self.pending_actions.pop(action_id)
            action["status"] = resolution
            return action
        raise ValueError(f"Action {action_id} not found in approval queue.")

    async def wait_for_resolution(self, action_id: str) -> str:
        """Wait for an action to be resolved and return the resolution string."""
        if action_id not in self.events:
            return "unknown"
        await self.events[action_id].wait()
        return self.resolutions.get(action_id, "unknown")

# Global unified queue instance
approval_queue = ApprovalQueueManager()
