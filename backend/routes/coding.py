from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from services.coding_orchestrator import coding_orchestrator

router = APIRouter(prefix="/api/kyron/coding", tags=["Coding"])

class ConnectProjectRequest(BaseModel):
    repo_path: str

class DispatchTaskRequest(BaseModel):
    task: str
    backend: str = "CodeAgent"  # "CodeAgent" or "opencode"

@router.post("/connect-project")
def connect_project(req: ConnectProjectRequest):
    try:
        return coding_orchestrator.connect_project(req.repo_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workers")
def get_workers():
    workers_list = []
    for wid, worker in coding_orchestrator.workers.items():
        workers_list.append({
            "worker_id": worker.worker_id,
            "task": worker.task,
            "backend": worker.backend,
            "status": worker.status,
            "worktree_path": worker.worktree_path,
            "created_at": worker.created_at,
            "action_id": worker.action_id
        })
    # Sort by newest first
    workers_list.sort(key=lambda x: x["created_at"], reverse=True)
    return {"success": True, "workers": workers_list, "connected_repo": coding_orchestrator.connected_repo}

@router.post("/dispatch")
async def dispatch_task(req: DispatchTaskRequest):
    if not req.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")
        
    try:
        return await coding_orchestrator.dispatch_task(req.task, req.backend)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{worker_id}")
def get_worker_logs(worker_id: str):
    if worker_id not in coding_orchestrator.workers:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    worker = coding_orchestrator.workers[worker_id]
    return {"success": True, "worker_id": worker_id, "status": worker.status, "logs": worker.logs}
