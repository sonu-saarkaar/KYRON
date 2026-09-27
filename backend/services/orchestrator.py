import json
import logging
import re
import uuid
import time
from typing import List, Dict, Any, Optional
from services.llm_client import LLMClient
from services.code_agent import CodeAgent, CodeAgentRunResult
from routes.system_control import execute_system_command, ExecuteSystemCommandRequest
from routes.browser_control import browser_control_agent, ExecuteBrowserCommandRequest

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    def __init__(self):
        # Local Ollama model for fast, private intent-classification
        self.routing_llm = LLMClient(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
            default_model="qwen2.5:0.5b" # Fast, lightweight local model
        )
        self.llm = LLMClient()
        self.code_agent = CodeAgent(workspace_dir=".", client=self.llm)

    async def route_command(self, command: str) -> Dict[str, Any]:
        """
        Receives user natural language, classifies intent via Ollama, 
        breaks down into sub-tasks, and routes to appropriate agents.
        """
        prompt = (
            "You are the KYRON Master Orchestrator Intent Router. "
            "Tum ek real human assistant ki tarah baat karo, robot ya script-reading machine ki tarah nahi. Casual, confident, friendly tone. Technical jargon avoid karo jab tak zaroori na ho.\n"
            "Your job is to analyze the user's natural language command (English, Hindi, or Hinglish) and break it down into a sequence of tasks for specialized agents.\n\n"
            "Available Agents:\n"
            "- CODE_AGENT: For modifying local codefiles, bug fixing, or analyzing workspace files.\n"
            "- BROWSER_AGENT: For web tasks, UI interaction on websites, checking things online.\n"
            "- SYSTEM_AGENT: For desktop OS tasks (like opening apps, notepad, calculator, sending WhatsApp/Slack messages, system volume, settings).\n\n"
            "Examples:\n"
            '- "notepad khol" -> agent: SYSTEM_AGENT, directive: "open notepad"\n'
            '- "fix bug in file.py" -> agent: CODE_AGENT, directive: "fix bug in file file.py"\n'
            '- "search news" -> agent: BROWSER_AGENT, directive: "search news"\n\n'
            "Return ONLY a valid JSON object strictly matching this schema:\n"
            "{\n"
            '  "tasks": [\n'
            '    {\n'
            '       "agent": "SYSTEM_AGENT",\n'
            '       "directive": "Exact sub-task for the agent"\n'
            '    }\n'
            '  ]\n'
            "}\n"
            "Note: 'agent' must be exactly one of: CODE_AGENT, BROWSER_AGENT, SYSTEM_AGENT.\n"
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Command: {command}"}
        ]

        try:
            res = await self.routing_llm.acomplete(messages=messages, temperature=0.1)
            if res.get("success") and res.get("content"):
                content = res["content"].strip()
                json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
                if json_match:
                    raw_json = json_match.group(1)
                else:
                    brace_match = re.search(r"(\{.*\})", content, re.DOTALL)
                    raw_json = brace_match.group(1) if brace_match else content
                routing_plan = json.loads(raw_json)
                tasks = routing_plan.get("tasks", [])
            else:
                tasks = self._fallback_route(command)
        except Exception as e:
            logger.error(f"Routing LLM error: {e}")
            tasks = self._fallback_route(command)
            
        if not tasks:
            return {"success": False, "message": "Failed to route command to any agent."}

        return await self.execute_plan(tasks)

    def _fallback_route(self, command: str) -> List[Dict[str, str]]:
        lower = command.lower()
        if "khol" in lower or "whatsapp" in lower or "notepad" in lower:
            return [{"agent": "SYSTEM_AGENT", "directive": command}]
        elif "amazon" in lower or "website" in lower or "search" in lower:
            return [{"agent": "BROWSER_AGENT", "directive": command}]
        else:
            return [{"agent": "CODE_AGENT", "directive": command}]

    async def execute_plan(self, tasks: List[Dict[str, str]]) -> Dict[str, Any]:
        """Executes sequence of tasks, passing through unified queue for safety gates."""
        session_id = f"sess-{uuid.uuid4().hex[:6]}"
        results = []
        requires_approval = False
        
        for idx, task in enumerate(tasks):
            agent = task.get("agent")
            directive = task.get("directive")
            logger.info(f"[Orchestrator {session_id}] Dispatching task {idx+1}/{len(tasks)} to {agent}: '{directive}'")
            
            step_res = {}
            if agent == "SYSTEM_AGENT":
                req = ExecuteSystemCommandRequest(command=directive)
                step_res = await execute_system_command(req)
                
            elif agent == "BROWSER_AGENT":
                # Assuming browser_control_agent is singleton and has parse_and_execute
                step_res = await browser_control_agent.parse_and_execute(directive)
                
            elif agent == "CODE_AGENT":
                # Basic code fix inference logic for Orchestrator (mocking file parse)
                # In real scenario, target_file/task would be parsed from directive
                # We do a basic run for demo purposes
                target_match = re.search(r"file ([\w\.]+)", directive)
                target = target_match.group(1) if target_match else "unknown_file.py"
                
                c_res: CodeAgentRunResult = self.code_agent.run(
                    target_file=target,
                    task=directive,
                    apply=False,
                    dry_run=True
                )
                
                step_res = {
                    "success": c_res.success,
                    "applied": c_res.applied,
                    "requires_confirmation": not c_res.applied and c_res.success,
                    "summary": c_res.summary,
                    "diff": c_res.diff
                }
                
                if step_res["requires_confirmation"]:
                    from services.approval_queue import approval_queue
                    action_id = approval_queue.register_pending_action(
                        agent_type="CODE",
                        description=f"Code fix for '{target}' via Orchestrator",
                        payload={"diff": c_res.diff, "summary": c_res.summary, "target_file": target, "task": directive, "status": "pending_confirmation"},
                        risk_level="medium"
                    )
                    step_res["action_id"] = action_id
                    step_res["pending_action"] = approval_queue.get_action(action_id)
            else:
                step_res = {"success": False, "message": f"Unknown agent: {agent}"}
                
            results.append({
                "agent": agent,
                "directive": directive,
                "result": step_res
            })
            
            if step_res.get("requires_confirmation"):
                requires_approval = True
                action_id = step_res.get("action_id")
                if action_id:
                    logger.info(f"[Orchestrator {session_id}] Task {idx+1} hit safety gate. Pausing sequence for approval of action {action_id}...")
                    from services.approval_queue import approval_queue
                    resolution = await approval_queue.wait_for_resolution(action_id)
                    logger.info(f"[Orchestrator {session_id}] Action {action_id} resolved with status: {resolution}")
                    
                    if not resolution.startswith("executed"):
                        logger.warning(f"[Orchestrator {session_id}] Action was rejected or failed. Aborting remaining sequence.")
                        break
                    else:
                        logger.info(f"[Orchestrator {session_id}] Action confirmed! Resuming sequence...")
                else:
                    logger.warning(f"[Orchestrator {session_id}] No action_id found to wait for. Aborting.")
                    break

        # Generate human voice vocalization summary for the executed tasks
        voice_summary = "Done Boss, tasks execute ho gaye hain."
        try:
            from utils.voice_formatter import format_voice_summary
            voice_summary = await format_voice_summary(results, context="Task plan execution completed")
        except Exception as e:
            logger.warning(f"Voice summary generation failed in Orchestrator: {e}")

        return {
            "success": True,
            "session_id": session_id,
            "tasks_total": len(tasks),
            "tasks_executed": len(results),
            "requires_approval": requires_approval,
            "results": results,
            "voice_vocalization": voice_summary
        }

master_orchestrator = MasterOrchestrator()
