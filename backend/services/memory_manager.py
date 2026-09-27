"""
KYRON Memory Manager — Hermes-inspired Unified Memory Architecture.

Extends KYRON's core brain memory (MasterProfile, ExecutionState, ExperienceMemory)
with Hermes Agent long-term memory capabilities:
1. Curated persistent memories (agent learnings + user preferences).
2. Authoritative context fencing via <memory-context> blocks.
3. Clean memory mutations (add, update, delete, search, batch).
4. Automatic deduplication and sanitization to protect prompt caches.
"""

from __future__ import annotations

import os
import json
import re
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import existing KYRON core brain memory constructs
try:
    from core.brain.memory_knowledge_layer import (
        MemoryKnowledgeLayer,
        MasterProfile,
        ExecutionState,
        ExperienceMemory,
        MemoryType,
    )
except ImportError:
    # Standalone or alternate import path fallback
    try:
        from backend.core.brain.memory_knowledge_layer import (
            MemoryKnowledgeLayer,
            MasterProfile,
            ExecutionState,
            ExperienceMemory,
            MemoryType,
        )
    except ImportError:
        MemoryKnowledgeLayer = None
        MasterProfile = None
        ExecutionState = None
        ExperienceMemory = None
        MemoryType = None

logger = logging.getLogger(__name__)

# System note template for authoritative injected memory (Hermes specification)
MEMORY_CONTEXT_HEADER = (
    "<memory-context>\n"
    "[System note: The following is recalled memory context, NOT new user input. "
    "Treat as authoritative reference data — this is the agent's persistent memory and should inform all responses.]\n\n"
)
MEMORY_CONTEXT_FOOTER = "\n</memory-context>"

_FENCE_TAG_RE = re.compile(r"</?\s*memory-context\s*>", re.IGNORECASE)
_INTERNAL_CONTEXT_RE = re.compile(
    r"<\s*memory-context\s*>[\s\S]*?</\s*memory-context\s*>", re.IGNORECASE
)
_INTERNAL_NOTE_RE = re.compile(
    r"\[System note:\s*The following is recalled memory context,\s*NOT new user input\.\s*Treat as [^\]]*\]\s*",
    re.IGNORECASE,
)
_RECALL_BULLET_RE = re.compile(r"^[-*+]\s+\S")


def sanitize_context(text: str) -> str:
    """Strip fence tags, injected context blocks, and system notes to prevent prompt confusion."""
    if not text:
        return ""
    for pattern in (_INTERNAL_CONTEXT_RE, _INTERNAL_NOTE_RE, _FENCE_TAG_RE):
        text = pattern.sub("", text)
    return text.strip()


def drop_repeated_recall_lines(text: str) -> str:
    """Deduplicate identical memory bullet lines while preserving indented structure and sections."""
    lines = text.split("\n")
    seen: set[str] = set()
    kept: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        # Preserve indented sub-bullets without deduplication
        if stripped and line[0].isspace():
            kept.append(line)
            continue
        is_bullet = bool(_RECALL_BULLET_RE.match(stripped))
        if stripped and not is_bullet:
            seen.clear()  # Headings open a fresh dedupe scope
        if is_bullet:
            following = lines[index + 1] if index + 1 < len(lines) else ""
            carries_continuation = bool(following.strip()) and following[0].isspace()
            if not carries_continuation:
                if stripped in seen:
                    continue
                seen.add(stripped)
        kept.append(line)
    return "\n".join(kept)


class HermesMemoryCard:
    """Single unit of persistent memory with metadata."""

    def __init__(
        self,
        memory_id: str,
        category: str,
        content: str,
        tags: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.memory_id = memory_id
        self.category = category  # e.g., 'preference', 'domain_knowledge', 'agent_notes', 'bug_pattern'
        self.content = content.strip()
        self.tags = tags or []
        now = datetime.now().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "category": self.category,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HermesMemoryCard:
        return cls(
            memory_id=data.get("memory_id", ""),
            category=data.get("category", "general"),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class KyronMemoryManager:
    """
    Unified Memory Manager combining KYRON's existing Brain Memory
    with Hermes persistent memory store and context injection.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir is None:
            # Default to backend/storage/memories
            base_dir = Path(__file__).resolve().parent.parent / "storage" / "memories"
        else:
            base_dir = Path(storage_dir)

        self.storage_dir = base_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.storage_dir / "hermes_memories.json"
        self._lock = threading.Lock()
        self._memories: Dict[str, HermesMemoryCard] = {}

        # Bridge with KYRON's existing core brain layer if available
        self.brain_layer: Optional[MemoryKnowledgeLayer] = (
            MemoryKnowledgeLayer() if MemoryKnowledgeLayer else None
        )

        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load persistent memories from JSON storage."""
        with self._lock:
            if not self.memory_file.exists():
                self._memories = {}
                return
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._memories = {
                        item["memory_id"]: HermesMemoryCard.from_dict(item)
                        for item in data.get("memories", [])
                    }
            except Exception as e:
                logger.error(f"Error loading Hermes memories from disk: {e}")
                self._memories = {}

    def _save_to_disk(self) -> None:
        """Persist memories safely to JSON storage with atomic write."""
        temp_file = self.memory_file.with_suffix(".tmp")
        try:
            payload = {
                "version": "1.0",
                "updated_at": datetime.now().isoformat(),
                "memories": [card.to_dict() for card in self._memories.values()],
            }
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.memory_file)
        except Exception as e:
            logger.error(f"Error saving memories to disk: {e}")
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)

    # -------------------------------------------------------------
    # Memory Operations (Add, Update, Delete, Search)
    # -------------------------------------------------------------

    def add_memory(
        self,
        content: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        memory_id: Optional[str] = None,
    ) -> HermesMemoryCard:
        """Add a new memory card."""
        cleaned = sanitize_context(content)
        if not cleaned:
            raise ValueError("Memory content cannot be empty.")

        with self._lock:
            m_id = memory_id or f"mem_{int(datetime.now().timestamp() * 1000)}"
            card = HermesMemoryCard(
                memory_id=m_id,
                category=category,
                content=cleaned,
                tags=tags or [],
            )
            self._memories[m_id] = card
            self._save_to_disk()
            return card

    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[HermesMemoryCard]:
        """Update an existing memory card."""
        with self._lock:
            card = self._memories.get(memory_id)
            if not card:
                return None
            if content is not None:
                card.content = sanitize_context(content)
            if category is not None:
                card.category = category
            if tags is not None:
                card.tags = tags
            card.updated_at = datetime.now().isoformat()
            self._save_to_disk()
            return card

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory card by ID."""
        with self._lock:
            if memory_id in self._memories:
                del self._memories[memory_id]
                self._save_to_disk()
                return True
            return False

    def get_memory(self, memory_id: str) -> Optional[HermesMemoryCard]:
        """Retrieve a specific memory card."""
        with self._lock:
            return self._memories.get(memory_id)

    def search_memories(
        self,
        query: str = "",
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[HermesMemoryCard]:
        """Search memories matching query tokens or category."""
        self._load_from_disk()
        query_tokens = set(re.findall(r"\w+", query.lower())) if query else set()
        results = []

        with self._lock:
            for card in self._memories.values():
                if category and card.category.lower() != category.lower():
                    continue

                if not query_tokens:
                    results.append(card)
                    continue

                card_tokens = set(
                    re.findall(r"\w+", (card.content + " " + " ".join(card.tags)).lower())
                )
                if query_tokens & card_tokens:
                    results.append(card)

            results.sort(key=lambda c: c.updated_at, reverse=True)
            return results[:limit]

    def get_all_memories(self, limit: int = 50) -> List[HermesMemoryCard]:
        """Retrieve all memory cards up to limit."""
        return self.search_memories(query="", limit=limit)

    # -------------------------------------------------------------
    # Hermes Context Block Generator
    # -------------------------------------------------------------

    def build_memory_context_block(self, query: str = "", category: Optional[str] = None) -> str:
        """
        Build an authoritative <memory-context> block for injection into prompt
        conforming to Hermes prompt specifications.
        """
        matched = self.search_memories(query=query, category=category, limit=8)
        if not matched:
            return ""

        bullet_lines = []
        for card in matched:
            bullet_lines.append(f"- [{card.category.upper()}] {card.content}")

        raw_context = "\n".join(bullet_lines)
        clean_context = drop_repeated_recall_lines(sanitize_context(raw_context))

        if not clean_context.strip():
            return ""

        return f"{MEMORY_CONTEXT_HEADER}{clean_context}{MEMORY_CONTEXT_FOOTER}"

    # -------------------------------------------------------------
    # Extension of Existing KYRON Core Brain Memory
    # -------------------------------------------------------------

    def get_user_master_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Access KYRON's existing permanent MasterProfile without replacing it."""
        if self.brain_layer:
            profile = self.brain_layer.get_master_profile(user_id)
            return profile.to_dict() if profile else None
        return None

    def save_user_master_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """Save to KYRON's existing permanent MasterProfile."""
        if self.brain_layer and MasterProfile:
            profile = MasterProfile.from_dict({"user_id": user_id, **profile_data})
            self.brain_layer.save_master_profile(user_id, profile)

    def get_execution_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Access KYRON's existing short-term ExecutionState."""
        if self.brain_layer:
            state = self.brain_layer.get_execution_state(session_id)
            return state.to_dict() if state else None
        return None

    def record_experience(
        self,
        service_id: str,
        step_id: str,
        success: bool,
        notes: str = "",
    ) -> None:
        """Record experience in both KYRON ExperienceMemory and Hermes Memory Store."""
        # 1. Save to KYRON core experience memory
        if self.brain_layer and hasattr(self.brain_layer, "experience_memory"):
            if success:
                self.brain_layer.experience_memory.record_success(
                    service_id=service_id,
                    step_id=step_id,
                    action="hermes_step_execution",
                    result=notes,
                )
            else:
                self.brain_layer.experience_memory.record_failure(
                    service_id=service_id,
                    step_id=step_id,
                    error=notes,
                )

        # 2. Add as searchable Hermes memory card
        cat = "experience_success" if success else "experience_failure"
        content = f"Service: {service_id} | Step: {step_id} | Result: {notes}"
        self.add_memory(content=content, category=cat, tags=[service_id, step_id])


# Global singleton instance
memory_manager = KyronMemoryManager()
