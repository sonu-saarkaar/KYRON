"""
KYRON LLM Client — Hermes-aligned High Performance LLM Gateway.

Supports:
1. Groq Cloud (Ultra-fast inference: qwen/qwen3.8-27b, llama models) via GROQ_API_KEY.
2. NVIDIA NIM API (https://integrate.api.nvidia.com/v1) via NVIDIA_API_KEY.
3. Hermes-style ToolMessage strict schema sanitization (strips 'name'/'tool_name' from tool messages).
4. Automatic fallback between providers so queries never hang or return canned errors.
"""

from __future__ import annotations

import os
import json
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from backend directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

import httpx
from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)

# Providers configuration
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"

NVIDIA_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_NVIDIA_MODEL = "nvidia/llama-3.1-nemotron-70b-instruct"


class LLMClient:
    """
    KYRON LLM Gateway supporting Groq, NVIDIA NIM, and OpenAI-compatible providers.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        # Force live disk read from .env files so running process always gets fresh keys
        from dotenv import dotenv_values
        file_env = {}
        for candidate in [
            Path(__file__).resolve().parent.parent / ".env",
            Path(__file__).resolve().parent.parent.parent / ".env",
            Path("c:/Users/pandi/Desktop/KYRON/backend/.env"),
            Path("c:/Users/pandi/Desktop/KYRON/.env")
        ]:
            if candidate.exists():
                try:
                    file_env.update(dotenv_values(candidate))
                except Exception:
                    pass

        def get_val(key: str, default: Optional[str] = None) -> Optional[str]:
            return file_env.get(key) or os.getenv(key) or default

        self.groq_api_key = get_val("GROQ_API_KEY")
        self.nvidia_api_key = api_key or get_val("NVIDIA_API_KEY")
        self.openai_api_key = get_val("OPENAI_API_KEY")
        configured_provider = (get_val("AI_PROVIDER") or "").lower()

        # Priority resolution
        if self.groq_api_key and (configured_provider == "groq" or not self.nvidia_api_key):
            self.provider = "groq"
            self.api_key = self.groq_api_key
            self.base_url = base_url or get_val("GROQ_BASE_URL", GROQ_BASE_URL)
            self.default_model = default_model or get_val("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        elif self.nvidia_api_key:
            self.provider = "nvidia"
            self.api_key = self.nvidia_api_key
            self.base_url = base_url or get_val("NVIDIA_BASE_URL", NVIDIA_NIM_BASE_URL)
            self.default_model = default_model or get_val("NVIDIA_MODEL", DEFAULT_NVIDIA_MODEL)
        else:
            self.provider = "openai"
            self.api_key = self.openai_api_key or "dummy_key_for_mock"
            self.base_url = base_url or get_val("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.default_model = default_model or get_val("OPENAI_MODEL", "gpt-4o-mini")

        timeout_client = httpx.Timeout(15.0, connect=5.0)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=timeout_client)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url, timeout=timeout_client)

        # Secondary backup client (Groq if primary is NVIDIA, or vice versa)
        self.backup_client = None
        self.backup_async_client = None
        self.backup_model = None
        if self.provider == "nvidia" and self.groq_api_key:
            self.backup_client = OpenAI(api_key=self.groq_api_key, base_url=GROQ_BASE_URL, timeout=timeout_client)
            self.backup_async_client = AsyncOpenAI(api_key=self.groq_api_key, base_url=GROQ_BASE_URL, timeout=timeout_client)
            self.backup_model = DEFAULT_GROQ_MODEL
        elif self.provider == "groq" and self.nvidia_api_key:
            self.backup_client = OpenAI(api_key=self.nvidia_api_key, base_url=NVIDIA_NIM_BASE_URL, timeout=timeout_client)
            self.backup_async_client = AsyncOpenAI(api_key=self.nvidia_api_key, base_url=NVIDIA_NIM_BASE_URL, timeout=timeout_client)
            self.backup_model = DEFAULT_NVIDIA_MODEL

    @staticmethod
    def sanitize_tool_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hermes standard: NVIDIA NIM strictly rejects 'name' or 'tool_name' in tool role messages.
        This method safely strips them copy-on-write.
        """
        sanitized = []
        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") == "tool":
                clean_msg = {k: v for k, v in msg.items() if k not in ("name", "tool_name")}
                sanitized.append(clean_msg)
            else:
                sanitized.append(msg)
        return sanitized

    def complete(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Synchronous chat completion with automatic provider fallback."""
        clean_messages = self.sanitize_tool_messages(messages)
        target_model = model or self.default_model

        call_args: Dict[str, Any] = {
            "model": target_model,
            "messages": clean_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        if tools:
            call_args["tools"] = tools

        try:
            response = self.client.chat.completions.create(**call_args)
            choice = response.choices[0]
            return {
                "success": True,
                "content": choice.message.content or "",
                "tool_calls": choice.message.tool_calls,
                "model": response.model,
                "provider": self.provider,
            }
        except Exception as e:
            logger.warning(f"Primary LLM ({self.provider}/{target_model}) error: {e}. Trying fallback models...")
            # Try alternate Groq models
            if self.provider == "groq":
                for alt_model in ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
                    if alt_model == target_model:
                        continue
                    try:
                        call_args["model"] = alt_model
                        response = self.client.chat.completions.create(**call_args)
                        choice = response.choices[0]
                        return {
                            "success": True,
                            "content": choice.message.content or "",
                            "tool_calls": choice.message.tool_calls,
                            "model": response.model,
                            "provider": "groq-fallback",
                        }
                    except Exception as fe:
                        logger.warning(f"Alternate Groq model {alt_model} failed: {fe}")

            if self.backup_client and self.backup_model:
                try:
                    call_args["model"] = self.backup_model
                    response = self.backup_client.chat.completions.create(**call_args)
                    choice = response.choices[0]
                    return {
                        "success": True,
                        "content": choice.message.content or "",
                        "tool_calls": choice.message.tool_calls,
                        "model": response.model,
                        "provider": "backup",
                    }
                except Exception as e2:
                    logger.error(f"Backup LLM error: {e2}")
            return {"success": False, "error": str(e), "content": ""}

    async def acomplete(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Asynchronous chat completion with automatic provider fallback."""
        clean_messages = self.sanitize_tool_messages(messages)
        target_model = model or self.default_model

        call_args: Dict[str, Any] = {
            "model": target_model,
            "messages": clean_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        if tools:
            call_args["tools"] = tools

        try:
            response = await self.async_client.chat.completions.create(**call_args)
            choice = response.choices[0]
            return {
                "success": True,
                "content": choice.message.content or "",
                "tool_calls": choice.message.tool_calls,
                "model": response.model,
                "provider": self.provider,
            }
        except Exception as e:
            logger.warning(f"Primary async LLM ({self.provider}/{target_model}) error: {e}. Trying fallback models...")
            # Try alternate Groq models
            if self.provider == "groq":
                for alt_model in ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
                    if alt_model == target_model:
                        continue
                    try:
                        call_args["model"] = alt_model
                        response = await self.async_client.chat.completions.create(**call_args)
                        choice = response.choices[0]
                        return {
                            "success": True,
                            "content": choice.message.content or "",
                            "tool_calls": choice.message.tool_calls,
                            "model": response.model,
                            "provider": "groq-fallback",
                        }
                    except Exception as fe:
                        logger.warning(f"Alternate async Groq model {alt_model} failed: {fe}")

            if self.backup_async_client and self.backup_model:
                try:
                    call_args["model"] = self.backup_model
                    response = await self.backup_async_client.chat.completions.create(**call_args)
                    choice = response.choices[0]
                    return {
                        "success": True,
                        "content": choice.message.content or "",
                        "tool_calls": choice.message.tool_calls,
                        "model": response.model,
                        "provider": "backup",
                    }
                except Exception as e2:
                    logger.error(f"Backup async LLM error: {e2}")
            return {"success": False, "error": str(e), "content": ""}


# Global singleton instance
llm_client = LLMClient()
