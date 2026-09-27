"""
KYRON Cron Scheduler — Hermes-inspired Scheduled Task Runner.

Enables KYRON to:
1. Schedule and automate recurring AI tasks (e.g. daily research summaries, periodic sanity checks).
2. Support cron expressions (e.g. '0 9 * * *' for 9 AM daily, '*/2 * * * *' for every 2 minutes)
   as well as interval seconds/minutes with croniter and fallback calculations.
3. Persist jobs to storage/cron/jobs.json.
4. Execute jobs asynchronously without blocking the FastAPI event loop.
5. Provide manual trigger ('run now') for instant verification.
"""

from __future__ import annotations

import os
import json
import asyncio
import logging
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    from croniter import croniter
except ImportError:
    croniter = None

logger = logging.getLogger(__name__)


class ScheduledJob:
    """Represents a scheduled cron task."""

    def __init__(
        self,
        job_id: str,
        name: str,
        prompt: str,
        schedule: str,
        enabled: bool = True,
        skills: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        last_run_at: Optional[str] = None,
        next_run_at: Optional[str] = None,
        run_count: int = 0,
        last_result: Optional[str] = None,
    ):
        self.job_id = job_id
        self.name = name
        self.prompt = prompt
        self.schedule = schedule  # Cron syntax e.g. "*/2 * * * *" or "interval:X"
        self.enabled = enabled
        self.skills = skills or []
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.last_run_at = last_run_at
        self.run_count = run_count
        self.last_result = last_result
        self.next_run_at = next_run_at or self.compute_next_run()

    def compute_next_run(self, from_time: Optional[datetime] = None) -> Optional[str]:
        """Compute next execution time from cron expression or interval."""
        base_time = from_time or datetime.now(timezone.utc)
        sched = self.schedule.strip()

        # Check if interval format: "interval:<seconds>"
        if sched.startswith("interval:"):
            try:
                secs = int(sched.split(":")[1])
                next_dt = base_time + timedelta(seconds=secs)
                return next_dt.isoformat()
            except Exception:
                pass

        # Use croniter for cron syntax
        if croniter:
            try:
                itr = croniter(sched, base_time)
                next_dt = itr.get_next(datetime)
                if next_dt.tzinfo is None:
                    next_dt = next_dt.replace(tzinfo=timezone.utc)
                return next_dt.isoformat()
            except Exception as e:
                logger.warning(f"croniter failed for schedule '{sched}': {e}")

        # Fallback for standard 5-part cron if croniter unavailable or interval
        # Default to 60 seconds interval fallback
        return (base_time + timedelta(minutes=1)).isoformat()

    def is_due(self, current_time: Optional[datetime] = None) -> bool:
        """Check if job is due for execution."""
        if not self.enabled or not self.next_run_at:
            return False
        now_dt = current_time or datetime.now(timezone.utc)
        try:
            next_dt = datetime.fromisoformat(self.next_run_at)
            if next_dt.tzinfo is None:
                next_dt = next_dt.replace(tzinfo=timezone.utc)
            return now_dt >= next_dt
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "name": self.name,
            "prompt": self.prompt,
            "schedule": self.schedule,
            "enabled": self.enabled,
            "skills": self.skills,
            "created_at": self.created_at,
            "last_run_at": self.last_run_at,
            "next_run_at": self.next_run_at,
            "run_count": self.run_count,
            "last_result": self.last_result,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ScheduledJob:
        return cls(
            job_id=data.get("job_id", ""),
            name=data.get("name", "unnamed-job"),
            prompt=data.get("prompt", ""),
            schedule=data.get("schedule", "* * * * *"),
            enabled=data.get("enabled", True),
            skills=data.get("skills", []),
            created_at=data.get("created_at"),
            last_run_at=data.get("last_run_at"),
            next_run_at=data.get("next_run_at"),
            run_count=data.get("run_count", 0),
            last_result=data.get("last_result"),
        )


class HermesScheduler:
    """
    Background Cron Task Runner and scheduler service.
    """

    def __init__(self, cron_dir: Optional[str] = None):
        if cron_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "storage" / "cron"
        else:
            base_dir = Path(cron_dir)

        self.cron_dir = base_dir
        self.cron_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_file = self.cron_dir / "jobs.json"
        self._jobs: Dict[str, ScheduledJob] = {}
        self._lock = threading.Lock()
        self._running = False
        self._runner_task: Optional[asyncio.Task] = None
        self._execution_handler: Optional[Callable[[ScheduledJob], Any]] = None

        self._load_jobs()

    def _load_jobs(self) -> None:
        """Load jobs from persistent storage."""
        with self._lock:
            if not self.jobs_file.exists():
                self._jobs = {}
                return
            try:
                with open(self.jobs_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._jobs = {
                        item["job_id"]: ScheduledJob.from_dict(item)
                        for item in data.get("jobs", [])
                    }
            except Exception as e:
                logger.error(f"Error loading cron jobs: {e}")
                self._jobs = {}

    def _save_jobs(self) -> None:
        """Save jobs atomically to disk."""
        temp_file = self.jobs_file.with_suffix(".tmp")
        try:
            payload = {
                "version": "1.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "jobs": [job.to_dict() for job in self._jobs.values()],
            }
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.jobs_file)
        except Exception as e:
            logger.error(f"Error saving cron jobs: {e}")
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)

    def set_execution_handler(self, handler: Callable[[ScheduledJob], Any]) -> None:
        """Attach custom execution handler (e.g. LLM agent invocation)."""
        self._execution_handler = handler

    def add_job(
        self,
        name: str,
        prompt: str,
        schedule: str,
        skills: Optional[List[str]] = None,
        job_id: Optional[str] = None,
    ) -> ScheduledJob:
        """Register a new scheduled task."""
        j_id = job_id or f"cron_{int(datetime.now().timestamp() * 1000)}"
        job = ScheduledJob(
            job_id=j_id,
            name=name,
            prompt=prompt,
            schedule=schedule,
            skills=skills or [],
        )
        with self._lock:
            self._jobs[j_id] = job
            self._save_jobs()
        logger.info(f"Added scheduled cron job: {name} ({schedule})")
        return job

    def delete_job(self, job_id: str) -> bool:
        """Delete job by ID."""
        with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                self._save_jobs()
                return True
            return False

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all registered jobs."""
        with self._lock:
            return [job.to_dict() for job in self._jobs.values()]

    async def execute_job(self, job: ScheduledJob) -> str:
        """Execute a single job and record execution timestamp and results."""
        now_iso = datetime.now(timezone.utc).isoformat()
        job.last_run_at = now_iso
        job.run_count += 1

        logger.info(f"Executing scheduled job '{job.name}' (id: {job.job_id})")

        try:
            if self._execution_handler:
                if asyncio.iscoroutinefunction(self._execution_handler):
                    result = await self._execution_handler(job)
                else:
                    result = self._execution_handler(job)
                output = str(result)
            else:
                # Default execution output
                output = f"Job '{job.name}' executed successfully at {now_iso} with prompt: {job.prompt[:80]}"
        except Exception as e:
            output = f"Execution error: {e}"
            logger.error(f"Error executing job {job.job_id}: {e}")

        job.last_result = output
        job.next_run_at = job.compute_next_run()

        with self._lock:
            self._jobs[job.job_id] = job
            self._save_jobs()

        return output

    async def trigger_now(self, job_id: str) -> Optional[str]:
        """Manually trigger a job immediately for testing or on-demand execution."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        return await self.execute_job(job)

    async def _tick(self) -> None:
        """Single tick iteration: find due jobs and execute."""
        now = datetime.now(timezone.utc)
        due_jobs = []
        with self._lock:
            for job in self._jobs.values():
                if job.is_due(now):
                    due_jobs.append(job)

        for job in due_jobs:
            await self.execute_job(job)

    async def start(self, poll_interval_seconds: float = 5.0) -> None:
        """Start background scheduler loop."""
        self._running = True
        logger.info(f"HermesScheduler background runner started (polling every {poll_interval_seconds}s).")
        while self._running:
            try:
                await self._tick()
            except Exception as e:
                logger.error(f"Error in scheduler tick: {e}")
            await asyncio.sleep(poll_interval_seconds)

    def stop(self) -> None:
        """Stop background scheduler loop."""
        self._running = False
        logger.info("HermesScheduler stopped.")


# Global singleton instance
scheduler = HermesScheduler()
