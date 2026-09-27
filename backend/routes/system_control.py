"""
KYRON SystemControlAgent Routes — REST API for Desktop OS-Level Actions.

Follows the Hermes & CodeAgent architectural patterns:
- POST /api/kyron/system-control/execute -> Parse command, run safe steps, pause if irreversible
- POST /api/kyron/system-control/confirm -> Execute paused irreversible action (Enter/Send)
- GET  /api/kyron/system-control/status  -> Check system control agent & active windows
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import logging
import re
import pygetwindow as gw

from services.system_control_agent import (
    system_control_agent,
    SystemControlError,
    WindowFocusError,
    AmbiguousContactError,
)
from services.llm_client import LLMClient

logger = logging.getLogger(__name__)
router = APIRouter()


class ExecuteSystemCommandRequest(BaseModel):
    command: str = Field(..., description="Natural language OS directive (e.g. 'Notepad khol aur Hello KYRON type kar')")


class ConfirmActionRequest(BaseModel):
    action_id: str = Field(..., description="Unique ID of the pending irreversible action")
    confirmed: bool = Field(True, description="True to confirm and send, False to reject/discard")


@router.get("/status")
def get_system_control_status():
    """Returns OS control subsystem status and list of open desktop windows."""
    try:
        open_windows = [w.title for w in gw.getAllWindows() if w.title and len(w.title.strip()) > 1]
    except Exception:
        open_windows = []

    return {
        "success": True,
        "agent": "KYRON SystemControlAgent",
        "desktop_platform": "Windows",
        "open_windows_count": len(open_windows),
        "open_windows": open_windows[:15],
        "pending_actions_count": len(system_control_agent.pending_actions),
        "safety_guardrails": {
            "window_focus_lock": True,
            "ambiguous_contact_abort": True,
            "irreversible_action_confirmation": True
        }
    }


@router.post("/execute")
async def execute_system_command(req: ExecuteSystemCommandRequest):
    """
    Parses natural language directive into OS steps, executes safe preparation steps,
    and pauses behind the Safety Gate if an irreversible action (sending message) is detected.
    """
    command_text = req.command.strip()
    if not command_text:
        raise HTTPException(status_code=400, detail="Command text cannot be empty.")

    logger.info(f"Parsing OS directive: '{command_text}'")

    # LLM Step Planning with fallback rule-based fast path
    client = LLMClient()
    lower = command_text.lower()

    # Fast path for power commands
    power_commands = {
        "shutdown": ["shutdown", "turn off", "laptop off", "band kar", "shut down", "power off"],
        "restart": ["restart", "reboot"],
        "sleep": ["sleep", "suspend"],
        "lock": ["lock"]
    }
    
    for cmd_type, keywords in power_commands.items():
        if any(keyword in lower for keyword in keywords):
            logger.info(f"Detected power command: {cmd_type}")
            res = system_control_agent.execute_power_command(cmd_type)
            return {
                "success": res.get("success", False),
                "summary": res.get("message", "Power command executed."),
                "voice_vocalization": f"Yes sir. {res.get('message', 'Executing power command.')}",
                "requires_confirmation": False
            }

    # YouTube/Song fast path
    if "youtube" in lower or "song" in lower or "gana" in lower or "gaana" in lower:
        import urllib.parse
        # Extract search query
        query = command_text.lower().replace("play", "").replace("song", "").replace("on youtube", "").replace("youtube", "").replace("mere liye", "").replace("banao", "").replace("bajao", "").replace("gana", "").replace("gaana", "").strip()
        if not query:
            query = "latest songs"
        
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        logger.info(f"Opening YouTube with query: {query}")
        
        # We can just use os.startfile to open the default browser natively
        import os
        try:
            os.startfile(search_url)
            return {
                "success": True,
                "summary": f"Opening YouTube for: {query}",
                "voice_vocalization": f"Playing {query} Boss.",
                "requires_confirmation": False
            }
        except Exception as e:
            logger.error(f"Failed to open YouTube: {e}")

    # Rule-based fast paths for standard commands
    is_whatsapp = "whatsapp" in lower
    is_notepad = "notepad" in lower
    is_calc = "calculator" in lower or "calc" in lower

    system_prompt = (
        "You are the KYRON SystemControlAgent planner. Convert user natural language directives into "
        "a sequence of desktop actions on Windows.\n"
        "Tum ek real human assistant ki tarah baat karo, robot ya script-reading machine ki tarah nahi. Casual, confident, friendly tone. Technical jargon avoid karo jab tak zaroori na ho.\n"
        "CRITICAL BEHAVIOR RULES:\n"
        "1. Jawab hamesha question ke scope ke barabar ho — chhote command ka chhota jawab.\n"
        "2. CASUAL 'DONE BOSS' CONFIRMATION: Jab bhi koi task complete ho, ek brief casual confirmation do.\n"
        "3. STRICT VOICE OUTPUT CONSTRAINT (voice_vocalization): MAX 1 short sentence. Sirf kaam ki baat bolo (e.g., 'Done Boss', 'Sending message Boss', 'Playing song'). Faltu details bilkul nahi.\n\n"
        "Available actions:\n"
        "- open_app (target: app name e.g. 'notepad', 'whatsapp', 'calculator', 'settings', 'display')\n"
        "- wait (seconds: number)\n"
        "- focus_window (target: window title string)\n"
        "- search_contact (target: contact name string - for chat apps)\n"
        "- type_text (text: string to type)\n"
        "- send_keys (key: e.g. 'enter')\n\n"
        "CRITICAL SAFETY RULE: Any action that sends messages or changes production state is IRREVERSIBLE. "
        "For messaging, DO NOT include the final 'enter' in steps. Mark requires_confirmation=true and populate pending_action.\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "summary": "Short summary",\n'
        '  "target_app": "App name",\n'
        '  "steps": [\n'
        '    {"action": "open_app", "target": "notepad"},\n'
        '    {"action": "focus_window", "target": "Notepad"},\n'
        '    {"action": "type_text", "text": "Hello"}\n'
        '  ],\n'
        '  "requires_confirmation": false,\n'
        '  "pending_action": null\n'
        "}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Directive: {command_text}"}
    ]

    plan = None
    try:
        res = await client.acomplete(messages=messages, temperature=0.2)
        if res.get("success") and res.get("content"):
            content = res["content"].strip()
            # extract JSON block if surrounded by markdown code fences
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
            raw_json = json_match.group(1) if json_match else content
            plan = json.loads(raw_json)
    except Exception as e:
        logger.warning(f"LLM planner parsing warning: {e}. Using deterministic fallback.")

    # Fallback plan generator if LLM response couldn't be parsed
    if not plan:
        if is_notepad:
            # Extract text to type
            text_to_type = "Hello KYRON"
            if "type" in lower:
                text_to_type = command_text.split("type", 1)[1].strip(" '\"kar")
            elif "aur" in lower:
                text_to_type = command_text.split("aur", 1)[1].strip(" '\"kar")

            plan = {
                "summary": f"Open Notepad and type '{text_to_type}'",
                "target_app": "notepad",
                "steps": [
                    {"action": "open_app", "target": "notepad"},
                    {"action": "wait", "seconds": 1.5},
                    {"action": "focus_window", "target": "Notepad"},
                    {"action": "type_text", "text": text_to_type}
                ],
                "requires_confirmation": False,
                "pending_action": None
            }
        elif is_whatsapp:
            # Parse recipient and message
            # e.g., "WhatsApp khol aur Sonu ko 'meeting at 5' bhej"
            recipient = "Contact"
            msg = "Hello"
            if "ko" in lower:
                parts = command_text.split("ko", 1)
                before_ko = parts[0]
                after_ko = parts[1]
                # recipient is the last word before 'ko'
                words = before_ko.strip().split()
                if words:
                    recipient = words[-1]
                # message is after 'ko'
                msg = after_ko.replace("bhej", "").replace("send", "").replace("likh", "").strip(" '\"")

            plan = {
                "summary": f"Draft WhatsApp message to {recipient}",
                "target_app": "whatsapp",
                "steps": [
                    {"action": "open_app", "target": "whatsapp"},
                    {"action": "wait", "seconds": 2.0},
                    {"action": "focus_window", "target": "WhatsApp"},
                    {"action": "search_contact", "target": recipient},
                    {"action": "type_text", "text": msg}
                ],
                "requires_confirmation": True,
                "pending_action": {
                    "app": "WhatsApp",
                    "target_contact": recipient,
                    "content": msg,
                    "description": f"Send WhatsApp message '{msg}' to {recipient}",
                    "final_step": {"action": "send_keys", "key": "enter"}
                }
            }
        else:
            plan = {
                "summary": f"Execute directive: {command_text}",
                "target_app": "calculator" if is_calc else "notepad",
                "steps": [
                    {"action": "open_app", "target": "calculator" if is_calc else "notepad"}
                ],
                "requires_confirmation": False,
                "pending_action": None
            }

    # Execute preparation steps with strict safety guardrails
    executed_steps = []
    current_app = plan.get("target_app", "")

    try:
        for step in plan.get("steps", []):
            action_type = step.get("action")
            logger.info(f"Executing step: {action_type} ({step})")

            if action_type == "open_app":
                target = step.get("target", current_app)
                system_control_agent.open_app(target)
                executed_steps.append(f"Opened application: {target}")

            elif action_type == "wait":
                import time as _t
                _t.sleep(float(step.get("seconds", 1.0)))

            elif action_type == "focus_window":
                win_query = step.get("target", current_app)
                # CRITICAL SAFETY: Aborts if window cannot be focused within timeout
                system_control_agent.find_and_focus_window(win_query, timeout=6.0)
                executed_steps.append(f"Focused window: {win_query}")

            elif action_type == "search_contact":
                contact = step.get("target")
                if not contact or len(contact.strip()) < 2:
                    raise AmbiguousContactError("SAFETY ABORT: Contact name was ambiguous or not provided.")
                system_control_agent.search_and_open_contact(contact, app_title=current_app or "WhatsApp")
                executed_steps.append(f"Located contact: {contact}")

            elif action_type == "type_text":
                text = step.get("text", "")
                # CRITICAL SAFETY: Verify window is still focused before typing
                system_control_agent.type_text(text, delay=0.04, verify_window=current_app)
                executed_steps.append(f"Typed text: '{text}'")

            elif action_type == "send_keys":
                key = step.get("key", "enter")
                system_control_agent.send_keys(key)
                executed_steps.append(f"Sent hotkey: {key}")

    except WindowFocusError as wfe:
        logger.error(f"Window focus safety abort: {wfe}")
        return {
            "success": False,
            "status": "focus_safety_aborted",
            "error_type": "WINDOW_FOCUS_ERROR",
            "message": str(wfe),
            "voice_vocalization": "Commander, target application window focus nahi ho payi. Accidental typing prevent karne ke liye action turant abort kar diya gaya hai.",
            "executed_steps": executed_steps,
            "requires_confirmation": False
        }
    except AmbiguousContactError as ace:
        logger.error(f"Ambiguous contact safety abort: {ace}")
        return {
            "success": False,
            "status": "clarification_needed",
            "error_type": "AMBIGUOUS_CONTACT_ERROR",
            "message": str(ace),
            "clarification_prompt": "Ambiguous contact detected or contact not found. Please provide the exact contact name or phone number.",
            "voice_vocalization": "Commander, contact confirm nahi ho paya ya multiple matches hain. Galat person ko message na jaye isliye maine pause kiya hai — kripya exact naam clarify kijiye.",
            "executed_steps": executed_steps,
            "requires_confirmation": False
        }
    except Exception as e:
        logger.error(f"OS Execution error: {e}")
        return {
            "success": False,
            "status": "execution_failed",
            "error_type": "EXECUTION_ERROR",
            "message": f"Action execution failed: {str(e)}",
            "executed_steps": executed_steps,
            "requires_confirmation": False
        }

    # Handle Safety Gate for Irreversible Actions
    registered_pending = None
    if plan.get("requires_confirmation") and plan.get("pending_action"):
        pending = plan["pending_action"]
        registered_pending = system_control_agent.register_pending_action(
            app=pending.get("app", current_app),
            target_contact=pending.get("target_contact"),
            content=pending.get("content", ""),
            final_step=pending.get("final_step", {"action": "send_keys", "key": "enter"}),
            description=pending.get("description", f"Send message to {pending.get('target_contact')}")
        )

    voice_msg = None
    if registered_pending:
        c_name = registered_pending.get("target_contact") or "contact"
        voice_msg = f"Commander, {c_name} ke liye message draft kar diya hai. Send karne ke liye confirm kijiye."
    else:
        voice_msg = f"Commander, {plan.get('summary', 'Directive')} successfully execute ho gaya."

    return {
        "success": True,
        "status": "waiting_confirmation" if registered_pending else "completed",
        "summary": plan.get("summary", "Directive executed"),
        "executed_steps": executed_steps,
        "requires_confirmation": bool(registered_pending),
        "pending_action": registered_pending,
        "voice_vocalization": voice_msg
    }


@router.post("/confirm")
def confirm_system_action(req: ConfirmActionRequest):
    """
    Physical user action gate: executes or discards the final irreversible step.
    """
    try:
        result = system_control_agent.confirm_and_execute(
            action_id=req.action_id,
            confirmed=req.confirmed
        )
        return result
    except Exception as e:
        logger.error(f"Confirmation execution error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
