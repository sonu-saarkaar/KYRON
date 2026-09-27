from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from services.orchestrator import master_orchestrator
from services.approval_queue import approval_queue

logger = logging.getLogger(__name__)
router = APIRouter()

class OrchestrateCommandRequest(BaseModel):
    command: str = Field(..., description="Natural language command (can be multi-agent)")

@router.post("/execute")
async def execute_orchestrator_command(req: OrchestrateCommandRequest):
    """
    Receives a high-level command, routes it via NIM LLM, and executes the sequence.
    Runs in background to prevent HTTP timeouts during safety gate pauses.
    """
    if not req.command.strip():
        raise HTTPException(status_code=400, detail="Command text cannot be empty.")
        
    try:
        import asyncio
        asyncio.create_task(master_orchestrator.route_command(req.command))
        return {"success": True, "message": "Command received and processing started.", "command": req.command}
    except Exception as e:
        logger.error(f"Orchestrator execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue")
def get_approval_queue():
    """
    Returns all pending actions across all agents that require physical confirmation.
    """
    return {
        "success": True,
        "pending_actions_count": len(approval_queue.get_all_pending()),
        "pending_actions": approval_queue.get_all_pending()
    }
