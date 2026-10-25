"""
KYRON - NVIDIA Brev & NVIDIA Agent Toolkit REST API Routes.

Endpoints:
- GET  /api/brev/status       -> Diagnostic info of Brev CLI, cloud health, and NVIDIA stack.
- GET  /api/brev/launchables  -> Catalog of pre-configured NVIDIA launchables (NemoClaw, Hermes, etc.).
- GET  /api/brev/instances    -> Active Brev cloud GPU instances.
- POST /api/brev/launch       -> Launch an environment (NemoClaw, Hermes, Isaac Sim).
- POST /api/brev/sandbox/run  -> Isolated sandbox execution conforming to OpenShell/NemoClaw.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from services.brev_nvidia_service import brev_nvidia_service

logger = logging.getLogger(__name__)
router = APIRouter()


class LaunchRequest(BaseModel):
    launchable_key: str = Field(..., description="Key or ID of launchable (e.g. 'nemoclaw', 'hermes', 'isaac_sim')")
    instance_name: Optional[str] = Field(None, description="Optional custom instance name")


class SandboxRunRequest(BaseModel):
    code: str = Field(..., description="Code snippet to execute in sandbox")
    language: Optional[str] = Field("python", description="Language of code (python)")


@router.get("/status")
def get_brev_status():
    """Returns Brev CLI and NVIDIA cloud status."""
    return brev_nvidia_service.get_status()


@router.get("/launchables")
def get_brev_launchables():
    """Returns the catalog of available NVIDIA Brev Launchables."""
    return {
        "success": True,
        "launchables": brev_nvidia_service.get_launchables()
    }


@router.get("/instances")
def list_brev_instances():
    """Lists running Brev GPU instances."""
    return brev_nvidia_service.list_instances()


@router.post("/launch")
def launch_brev_environment(req: LaunchRequest):
    """Prepares and launches an NVIDIA Launchable environment."""
    if not req.launchable_key.strip():
        raise HTTPException(status_code=400, detail="Launchable key cannot be empty.")
    res = brev_nvidia_service.launch_environment(req.launchable_key, req.instance_name)
    return res


@router.post("/sandbox/run")
def execute_in_sandbox(req: SandboxRunRequest):
    """Executes code in isolated NemoClaw / OpenShell sandbox."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    res = brev_nvidia_service.execute_in_sandbox(req.code, language=req.language or "python")
    return res
