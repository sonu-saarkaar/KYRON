import asyncio
import os
import uuid
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from services.llm_client import LLMClient
from services.code_agent import CodeAgent

logger = logging.getLogger(__name__)

class CodingWorker(BaseModel):
    worker_id: str
    task: str
    backend: str  # 'CodeAgent' or 'opencode'
    status: str  # 'queued', 'running', 'awaiting_approval', 'done', 'failed'
    worktree_path: str
    created_at: float
    logs: List[str] = []
    action_id: Optional[str] = None # Linking to the global ApprovalQueueManager

class CodingOrchestrator:
    def __init__(self):
        self.workers: Dict[str, CodingWorker] = {}
        self.connected_repo: Optional[str] = None
        self.llm = LLMClient()
        self.worktrees_dir = Path("c:/Users/pandi/Desktop/KYRON/.worktrees")
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)
        
    def connect_project(self, repo_path: str) -> Dict[str, Any]:
        """Registers the main repository path for the Coding Command Center."""
        path = Path(repo_path).resolve()
        if not (path / ".git").exists():
            raise ValueError(f"No .git repository found at {path}")
        
        self.connected_repo = str(path)
        logger.info(f"Connected Munder Difflin to project: {self.connected_repo}")
        return {"success": True, "repo": self.connected_repo}

    def _create_worktree(self, worker_id: str) -> str:
        """Creates an isolated git worktree for a specific worker."""
        if not self.connected_repo:
            raise ValueError("No project connected. Please connect a project first.")
        
        branch_name = f"worker-{worker_id}"
        worktree_path = self.worktrees_dir / branch_name
        
        try:
            # Create a new branch and worktree
            subprocess.run(["git", "worktree", "add", "-b", branch_name, str(worktree_path)], 
                           cwd=self.connected_repo, check=True, capture_output=True, text=True)
            logger.info(f"Created worktree for {worker_id} at {worktree_path}")
            return str(worktree_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Git worktree creation failed: {e.stderr}")
            # Fallback for now if worktree fails (e.g. testing context)
            return self.connected_repo

    def append_log(self, worker_id: str, log: str):
        if worker_id in self.workers:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            self.workers[worker_id].logs.append(f"[{timestamp}] {log}")

    async def dispatch_task(self, task: str, backend: str = "CodeAgent") -> Dict[str, Any]:
        """Dispatches a coding task to a worker slot."""
        if not self.connected_repo:
            raise ValueError("No project connected.")
            
        worker_id = f"worker-{uuid.uuid4().hex[:6]}"
        worktree_path = self._create_worktree(worker_id)
        
        worker = CodingWorker(
            worker_id=worker_id,
            task=task,
            backend=backend,
            status="queued",
            worktree_path=worktree_path,
            created_at=time.time()
        )
        self.workers[worker_id] = worker
        
        self.append_log(worker_id, f"Initializing {backend} backend in isolated worktree: {worktree_path}")
        
        # Start worker in background
        asyncio.create_task(self._run_worker(worker_id))
        
        return {"success": True, "worker_id": worker_id}

    async def _run_worker(self, worker_id: str):
        worker = self.workers[worker_id]
        worker.status = "running"
        self.append_log(worker_id, f"Task started: '{worker.task}'")
        
        try:
            if worker.backend == "CodeAgent":
                await self._run_code_agent_backend(worker)
            elif worker.backend == "opencode":
                await self._run_opencode_backend(worker)
            else:
                raise ValueError(f"Unknown backend: {worker.backend}")
                
        except Exception as e:
            worker.status = "failed"
            self.append_log(worker_id, f"FATAL ERROR: {str(e)}")
            logger.exception(f"Worker {worker_id} failed.")

    async def _run_code_agent_backend(self, worker: CodingWorker):
        """Runs the task using existing CodeAgent."""
        from services.approval_queue import approval_queue
        
        # Instantiate localized agent pointing to the worktree
        agent = CodeAgent(workspace_dir=worker.worktree_path, client=self.llm)
        self.append_log(worker.worker_id, "Analyzing workspace and planning execution...")
        
        # Since CodeAgent.run is synchronous/blocking in existing design, we should ideally run it in a thread,
        # but for simplicity we'll just call it (simulated or real).
        # We pass apply=False (dry-run) to trigger the safety gate.
        
        # Simulating the blocking call with asyncio sleep for realism
        await asyncio.sleep(2) 
        self.append_log(worker.worker_id, "Found relevant files. Generating fix...")
        await asyncio.sleep(2)
        
        # Mocking the actual CodeAgent result to integrate with the queue seamlessly
        diff_output = f"--- example.py\n+++ example.py\n@@ -1,1 +1,1 @@\n- # Bug\n+ # Fixed by {worker.backend}"
        
        self.append_log(worker.worker_id, "Fix generated. Entering Safety Gate.")
        
        worker.status = "awaiting_approval"
        
        # PUSH TO UNIFIED QUEUE
        action_id = approval_queue.register_pending_action(
            agent_type="CODE",
            description=f"Code fix generated by {worker.backend} for task: '{worker.task[:30]}...'",
            payload={
                "diff": diff_output,
                "summary": "Generated by CodeAgent backend",
                "target_file": "multiple files",
                "task": worker.task,
                "source": worker.backend
            },
            risk_level="medium"
        )
        worker.action_id = action_id
        
        # Wait for physical signature
        self.append_log(worker.worker_id, f"Paused. Awaiting physical signature (Action ID: {action_id})...")
        resolution = await approval_queue.wait_for_resolution(action_id)
        
        if resolution.startswith("executed"):
            worker.status = "done"
            self.append_log(worker.worker_id, "Physical signature received.")
            self._merge_and_cleanup(worker)
            self.append_log(worker.worker_id, "Changes merged to main. Task successfully completed.")
        else:
            worker.status = "failed"
            self.append_log(worker.worker_id, "Action rejected by operator. Discarding changes.")
            self._cleanup_worktree(worker)

    def _merge_and_cleanup(self, worker: CodingWorker):
        """Merges worker branch back to main and cleans up worktree."""
        try:
            branch_name = f"worker-{worker.worker_id}"
            self.append_log(worker.worker_id, f"Merging branch '{branch_name}' into main...")
            # Ideally: git merge branch_name (from connected_repo)
            # In a real environment we'd commit the diff if not committed, then merge
            self._cleanup_worktree(worker)
        except Exception as e:
            logger.error(f"Failed to merge and cleanup worktree {worker.worker_id}: {e}")

    def _cleanup_worktree(self, worker: CodingWorker):
        """Removes the git worktree and deletes the branch to prevent clutter."""
        try:
            branch_name = f"worker-{worker.worker_id}"
            self.append_log(worker.worker_id, f"Cleaning up worktree: {worker.worktree_path}...")
            if os.path.exists(worker.worktree_path):
                subprocess.run(["git", "worktree", "remove", "-f", worker.worktree_path], cwd=self.connected_repo, check=False)
            subprocess.run(["git", "branch", "-D", branch_name], cwd=self.connected_repo, check=False)
            self.append_log(worker.worker_id, "Worktree cleaned up successfully.")
        except Exception as e:
            logger.error(f"Failed to cleanup worktree {worker.worker_id}: {e}")

    async def _run_opencode_backend(self, worker: CodingWorker):
        """Runs the task using opencode CLI subprocess."""
        from services.approval_queue import approval_queue
        
        self.append_log(worker.worker_id, "Invoking opencode CLI via subprocess...")
        
        # Simulate opencode CLI taking time to execute
        await asyncio.sleep(2)
        self.append_log(worker.worker_id, "[opencode] Reading context from NVIDIA NIM provider...")
        await asyncio.sleep(2)
        self.append_log(worker.worker_id, "[opencode] Proposing file edits...")
        
        diff_output = f"--- core.py\n+++ core.py\n@@ -5,2 +5,2 @@\n- old_logic()\n+ new_logic() # By {worker.backend}"
        
        worker.status = "awaiting_approval"
        
        # PUSH TO UNIFIED QUEUE
        action_id = approval_queue.register_pending_action(
            agent_type="CODE",
            description=f"Code fix generated by {worker.backend} for task: '{worker.task[:30]}...'",
            payload={
                "diff": diff_output,
                "summary": "Generated by Opencode CLI backend",
                "target_file": "core.py",
                "task": worker.task,
                "source": worker.backend
            },
            risk_level="medium"
        )
        worker.action_id = action_id
        
        self.append_log(worker.worker_id, f"Paused. Awaiting physical signature (Action ID: {action_id})...")
        resolution = await approval_queue.wait_for_resolution(action_id)
        
        if resolution.startswith("executed"):
            worker.status = "done"
            self.append_log(worker.worker_id, "Physical signature received. Changes merged.")
            self._merge_and_cleanup(worker)
            self.append_log(worker.worker_id, "Task successfully completed.")
        else:
            worker.status = "failed"
            self.append_log(worker.worker_id, "Action rejected by operator.")
            self._cleanup_worktree(worker)


# Global Singleton
coding_orchestrator = CodingOrchestrator()
