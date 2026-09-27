"""
KYRON CodeAgent Routes — REST API for Autonomous Code Execution & Repair.

Follows the Hermes routes architecture pattern:
- POST /api/kyron/code-agent/run      -> Execute autonomous bug fix loop
- GET  /api/kyron/code-agent/status   -> Check sandbox & agent runtime status
- POST /api/kyron/code-agent/command  -> Execute command inside sandbox
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path

from services.code_agent import CodeAgent, SandboxEnvironment, code_agent
from services.llm_client import llm_client

router = APIRouter()


class RunCodeAgentRequest(BaseModel):
    task: str = Field(..., description="Description of the bug or task to resolve")
    target_file: str = Field(..., description="Relative path of file to fix inside workspace")
    test_command: str = Field(..., description="Command to execute to verify test passing")
    workspace_dir: Optional[str] = Field(None, description="Optional custom workspace directory")
    max_iterations: int = Field(5, ge=1, le=10, description="Max self-correction retry attempts")
    diagnostic_hint: Optional[str] = Field(None, description="Optional context or hint for the LLM")
    use_docker: bool = Field(False, description="Attempt Docker isolation if available")
    apply: bool = Field(False, description="Explicit confirmation gate. If False (default), executes as safe dry run without modifying files.")
    dry_run: Optional[bool] = Field(None, description="Optional dry run override.")


class ExecuteCommandRequest(BaseModel):
    command: str
    workspace_dir: Optional[str] = None
    timeout: int = 30


@router.get("/status")
def get_code_agent_status():
    """Check CodeAgent runtime, Docker availability, and LLM provider."""
    sandbox = code_agent.sandbox
    return {
        "success": True,
        "agent": "KYRON CodeAgent (OpenHands Selective Port)",
        "workspace_dir": str(sandbox.workspace_dir),
        "docker_available": sandbox.docker_available,
        "default_mode": "docker_sandbox" if sandbox.docker_available else "local_sandbox",
        "llm_provider": llm_client.provider,
        "llm_model": llm_client.default_model,
        "safety_gate": {
            "default_mode": "dry_run",
            "apply_required": True,
            "description": "Files remain untouched unless explicit apply=true is sent."
        }
    }


@router.post("/run")
def run_code_agent(req: RunCodeAgentRequest):
    """
    Run autonomous ReAct self-correction loop to diagnose and fix a failing test/bug.
    By default runs in safe Dry-Run mode unless apply=True is specified.
    """
    workspace = req.workspace_dir or str(code_agent.sandbox.workspace_dir)
    agent = CodeAgent(
        workspace_dir=workspace,
        client=llm_client,
        max_iterations=req.max_iterations,
        use_docker=req.use_docker,
    )

    result = agent.run_fix_loop(
        task_description=req.task,
        target_file=req.target_file,
        test_command=req.test_command,
        diagnostic_hint=req.diagnostic_hint,
        apply=req.apply,
        dry_run=req.dry_run,
    )

    response_data = {
        "success": result.success,
        "applied": result.applied,
        "requires_confirmation": not result.applied and result.success,
        "iterations": result.iterations,
        "summary": result.summary,
        "diff": result.diff,
        "proposed_code": result.proposed_code,
        "files_modified": result.files_modified,
        "final_test_output": result.final_test_output,
        "trajectory": result.trajectory,
    }

    if response_data["requires_confirmation"]:
        from services.approval_queue import approval_queue
        import time
        action_id = approval_queue.register_pending_action(
            agent_type="CODE",
            description=f"Code fix for '{req.target_file}'",
            payload={
                "diff": result.diff,
                "summary": result.summary,
                "target_file": req.target_file,
                "task": req.task,
                "test_command": req.test_command,
                "created_at": time.time(),
                "status": "pending_confirmation"
            },
            risk_level="medium"
        )
        response_data["action_id"] = action_id

    return response_data


@router.post("/command")
def execute_sandbox_command(req: ExecuteCommandRequest):
    """Execute arbitrary command in sandbox environment."""
    workspace = req.workspace_dir or str(code_agent.sandbox.workspace_dir)
    sandbox = SandboxEnvironment(workspace_dir=workspace)
    res = sandbox.execute_command(req.command, timeout=req.timeout)
    return {
        "success": res["exit_code"] == 0,
        "result": res,
    }
