"""
KYRON BrowserControlAgent Routes — REST API for Generic Browser Automation.

Endpoints:
- POST /api/kyron/browser/execute  -> Receive natural language directive, run reversible steps, pause if irreversible
- POST /api/kyron/browser/confirm  -> Physical user gate: execute or reject pending irreversible action
- GET  /api/kyron/browser/status   -> Inspect browser session, active page, and pending confirmation items
- GET  /api/kyron/browser/activity -> Stream real-time telemetry log for ActivityFeed
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from services.browser_control_agent import browser_control_agent

logger = logging.getLogger(__name__)
router = APIRouter()


class ExecuteBrowserCommandRequest(BaseModel):
    command: str = Field(..., description="Natural language web directive (e.g. 'Gmail khol aur unread count bata')")
    max_steps: Optional[int] = Field(10, ge=1, le=25, description="Max automation steps before completing")


class ConfirmBrowserActionRequest(BaseModel):
    action_id: str = Field(..., description="Unique ID of the pending irreversible action")
    confirmed: bool = Field(True, description="True to execute the final click/submit, False to reject")


@router.get("/status")
async def get_browser_status():
    """Inspect current browser state, active URL, page title, and pending safety gate actions."""
    try:
        return await browser_control_agent.get_status()
    except Exception as e:
        logger.error(f"Error getting browser status: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent": "KYRON BrowserControlAgent",
            "browser_ready": False
        }


@router.get("/activity")
def get_browser_activity():
    """Returns recent browser activity telemetry for ActivityFeed."""
    return {
        "success": True,
        "activity": browser_control_agent.activity_log[-20:]
    }


@router.post("/execute")
async def execute_browser_command(req: ExecuteBrowserCommandRequest):
    """
    Executes a web automation directive.
    - REVERSIBLE actions (navigate, scroll, read, search, type): Auto-execute immediately.
    - IRREVERSIBLE actions (submit, pay, checkout, buy, delete): PAUSES and returns ActionPreviewCard payload.
    """
    command = req.command.strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command cannot be empty.")

    logger.info(f"Browser directive received: '{command}'")

    try:
        result = await browser_control_agent.execute_task(
            directive=command,
            max_steps=req.max_steps or 10
        )
        return result
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Browser execution failed: {e}\n{tb}")
        err_msg = str(e) or repr(e)
        return {
            "success": False,
            "status": "execution_failed",
            "error_type": "BROWSER_EXECUTION_ERROR",
            "message": f"{type(e).__name__}: {err_msg}",
            "traceback": tb.splitlines()[-3:],
            "voice_vocalization": "Commander, browser directive execution me error aaya hai."
        }


@router.post("/confirm")
async def confirm_browser_action(req: ConfirmBrowserActionRequest):
    """
    Physical user action gate: executes or rejects the final irreversible browser action.
    """
    try:
        result = await browser_control_agent.confirm_action(
            action_id=req.action_id,
            confirmed=req.confirmed
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Browser confirmation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
