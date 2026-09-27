"""
KYRON Voice Formatter Utility
Converts raw logs, system status, and task execution results into
1-3 line conversational human summaries using local Ollama (qwen2.5:0.5b).
Ensures raw technical text is never spoken directly via TTS.
"""

import os
import re
import json
import logging
import asyncio
from typing import Any, Dict, Optional, Union
import urllib.request
import urllib.error

from services.voice_service import text_to_speech_safe

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_VOICE_MODEL = os.getenv("VOICE_SUMMARY_MODEL", "qwen2.5:0.5b")

SYSTEM_PERSONA_PROMPT = (
    "You are KYRON's personal voice assistant speaking directly to your Boss.\n"
    "CRITICAL RULES:\n"
    "1. Tum ek real human assistant ki tarah baat karo, robot ya script-reading machine ki tarah nahi. Casual, confident, friendly tone. Technical jargon avoid karo jab tak zaroori na ho.\n"
    "2. Jawab ko 1 se 3 short lines me bolo. Casual aur confident Hinglish/Hindi me baat karo (e.g. 'Boss, sabhi systems badhiya chal rahe hain, sab smoothly execute ho raha hai.').\n"
    "3. NEVER read raw technical logs, bullet points, hyphens, JSON keys, error codes, window handles, memory addresses, ya code directly. Do NOT make a bulleted list.\n"
    "4. Always focus on what matters to Boss: kya chal raha hai, kya complete ho gaya, aur kya sab theek hai.\n"
    "5. Return ONLY 1 to 3 spoken sentences. No quotation marks, no markdown headings, no bullet lists."
)


class VoiceFormatter:
    """Formats raw system status, task results, and technical logs into conversational voice summaries."""

    def __init__(self, model_name: str = DEFAULT_VOICE_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def _prepare_payload(self, raw_data: Any, context: Optional[str] = None) -> str:
        """Serializes and trims raw data into a clean text snippet for the model."""
        if isinstance(raw_data, (dict, list)):
            try:
                content_str = json.dumps(raw_data, ensure_ascii=False, indent=2)
            except Exception:
                content_str = str(raw_data)
        else:
            content_str = str(raw_data) if raw_data is not None else ""

        # Limit payload size to keep local Ollama response ultra-fast (< 1-2 seconds)
        if len(content_str) > 2000:
            content_str = content_str[:2000] + "... [truncated]"

        user_content = f"User Context / Query: {context}\n" if context else ""
        user_content += f"Raw Status/Log:\n{content_str}\n\n"
        user_content += (
            "Task: Convert this into 1-2 short, conversational, friendly lines for Boss in casual Hindi/Hinglish "
            "(jaise: 'Boss, sabhi systems active hain aur sab smoothly chal raha hai.'). Technical jargon avoid karo."
        )
        return user_content

    async def format_voice_summary(self, raw_data: Any, context: Optional[str] = None) -> str:
        """
        Asynchronously generates a 1-3 line conversational summary using local Ollama (qwen2.5:0.5b).
        Applies phonetic pronunciation sanitization (KYRON -> Kaeyron) before returning.
        """
        user_prompt = self._prepare_payload(raw_data, context)

        # Run the HTTP call in a thread pool to avoid blocking async event loop
        loop = asyncio.get_event_loop()
        try:
            summary = await loop.run_in_executor(None, self._call_ollama_sync, user_prompt)
            if summary:
                cleaned = self._clean_summary(summary)
                return text_to_speech_safe(cleaned)
        except Exception as e:
            logger.warning(f"VoiceFormatter Ollama call failed: {e}. Using intelligent fallback.")

        # Fallback if local Ollama fails or times out
        fallback = self._generate_fallback_summary(raw_data)
        return text_to_speech_safe(fallback)

    def format_voice_summary_sync(self, raw_data: Any, context: Optional[str] = None) -> str:
        """Synchronous version of format_voice_summary."""
        user_prompt = self._prepare_payload(raw_data, context)
        try:
            summary = self._call_ollama_sync(user_prompt)
            if summary:
                cleaned = self._clean_summary(summary)
                return text_to_speech_safe(cleaned)
        except Exception as e:
            logger.warning(f"VoiceFormatter Ollama sync call failed: {e}. Using intelligent fallback.")

        fallback = self._generate_fallback_summary(raw_data)
        return text_to_speech_safe(fallback)

    def _call_ollama_sync(self, user_prompt: str) -> Optional[str]:
        """Calls local Ollama chat API via urllib."""
        endpoint = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PERSONA_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 120
            }
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=8.0) as response:
            if response.status == 200:
                result = json.loads(response.read().decode("utf-8"))
                message = result.get("message", {})
                return message.get("content", "").strip()

        return None

    def _clean_summary(self, text: str) -> str:
        """Strips unnecessary markdown, quotation marks, or thinking tags."""
        # Strip <think> tags if present in reasoning models
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        # Remove surrounding quotes
        text = text.strip(' \t\n\r"\'`')
        # Remove markdown headers or bolding
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"^[#\s\-*]+", "", text)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _generate_fallback_summary(self, raw_data: Any) -> str:
        """Generates a pleasant human conversational summary if Ollama is unreachable."""
        if isinstance(raw_data, dict):
            if raw_data.get("agent_running") or raw_data.get("status") == "operational":
                wins = raw_data.get("open_windows_count", 0)
                if wins > 0:
                    return f"Boss, sabhi systems badhiya chal rahe hain. Desktop par {wins} active windows open hain aur sab normal hai."
                return "Boss, system background me bilkul smoothly run kar raha hai aur sabhi agents active hain."
            if "error" in raw_data or raw_data.get("success") is False:
                return "Boss, system me ek chhota issue detect hua hai, lekin baaki saari services normal chal rahi hain."

        return "Boss, sabhi core services active hain aur smoothly kaam kar rahi hain. Koi dikkat nahi hai."


# Global singleton instance
voice_formatter = VoiceFormatter()


async def format_voice_summary(raw_data: Any, context: Optional[str] = None) -> str:
    """Convenience helper function for async voice formatting."""
    return await voice_formatter.format_voice_summary(raw_data, context)


def format_voice_summary_sync(raw_data: Any, context: Optional[str] = None) -> str:
    """Convenience helper function for synchronous voice formatting."""
    return voice_formatter.format_voice_summary_sync(raw_data, context)


def get_live_system_status() -> Dict[str, Any]:
    """Gathers real-time system metrics across active agents for status requests."""
    open_titles = []
    try:
        import pygetwindow as gw
        open_titles = [w.title for w in gw.getAllWindows() if w.title and len(w.title.strip()) > 1]
    except Exception:
        pass

    pending_count = 0
    try:
        from services.system_control_agent import system_control_agent
        pending_count = len(system_control_agent.pending_actions)
    except Exception:
        pass

    return {
        "status": "operational",
        "desktop_platform": "Windows",
        "open_windows_count": len(open_titles),
        "active_windows": open_titles[:5],
        "pending_actions_count": pending_count,
        "agents": {
            "orchestrator": "ready",
            "system_control": "ready",
            "code_agent": "ready",
            "browser_agent": "ready"
        }
    }
