"""
KYRON Skills Engine — Hermes-inspired Skills-from-Experience System.

Enables KYRON AI Agent to:
1. Learn reusable skills from solved tasks or user instructions.
2. Structure skills following Hermes HARDLINE standards (name, description <=60 chars,
   when to use, prerequisites, canonical procedure, verification).
3. Persist skills in storage/skills/ as modular, reusable skill definitions.
4. Dynamically route and inject matched skills into agent turns so past problem
   solutions (e.g., 'BookMyGaadi bugs check') are seamlessly reused across sessions.
"""

from __future__ import annotations

import os
import json
import re
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class HermesSkill:
    """Represents an agent skill learned from experience or authored."""

    def __init__(
        self,
        name: str,
        description: str,
        trigger_phrases: List[str],
        procedure: List[str],
        prerequisites: Optional[List[str]] = None,
        verification: str = "",
        tags: Optional[List[str]] = None,
        version: str = "0.1.0",
        author: str = "KYRON-Hermes",
        created_at: Optional[str] = None,
    ):
        # Hermes authoring standard: lowercase-hyphenated name
        self.name = re.sub(r"[^a-z0-9\-]", "-", name.lower().strip()).strip("-")
        # Hermes standard: concise description (<=60 chars if possible)
        self.description = description.strip()
        self.trigger_phrases = [tp.strip().lower() for tp in trigger_phrases if tp.strip()]
        self.procedure = [p.strip() for p in procedure if p.strip()]
        self.prerequisites = prerequisites or []
        self.verification = verification.strip()
        self.tags = tags or []
        self.version = version
        self.author = author
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "trigger_phrases": self.trigger_phrases,
            "procedure": self.procedure,
            "prerequisites": self.prerequisites,
            "verification": self.verification,
            "tags": self.tags,
            "version": self.version,
            "author": self.author,
            "created_at": self.created_at,
        }

    def to_markdown(self) -> str:
        """Render skill in Hermes SKILL.md format with frontmatter."""
        prereqs = "\n".join([f"- {p}" for p in self.prerequisites]) if self.prerequisites else "- None"
        triggers = "\n".join([f"- \"{t}\"" for t in self.trigger_phrases])
        steps = "\n".join([f"{i+1}. {step}" for i, step in enumerate(self.procedure)])

        return f"""---
name: {self.name}
description: "{self.description}"
version: {self.version}
author: {self.author}
tags: {json.dumps(self.tags)}
---

# {self.name.replace('-', ' ').title()}

{self.description}

## When to Use
{triggers}

## Prerequisites
{prereqs}

## Procedure
{steps}

## Verification
{self.verification or "Check outputs for expected return status."}
"""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HermesSkill:
        return cls(
            name=data.get("name", "unnamed-skill"),
            description=data.get("description", ""),
            trigger_phrases=data.get("trigger_phrases", []),
            procedure=data.get("procedure", []),
            prerequisites=data.get("prerequisites", []),
            verification=data.get("verification", ""),
            tags=data.get("tags", []),
            version=data.get("version", "0.1.0"),
            author=data.get("author", "KYRON-Hermes"),
            created_at=data.get("created_at"),
        )


class SkillsEngine:
    """
    Manages discovery, learning, extraction, and execution routing of skills.
    """

    def __init__(self, skills_dir: Optional[str] = None):
        if skills_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "storage" / "skills"
        else:
            base_dir = Path(skills_dir)

        self.skills_dir = base_dir
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._skills_cache: Dict[str, HermesSkill] = {}
        self._lock = threading.Lock()
        self.load_all_skills()

    def load_all_skills(self) -> None:
        """Scan skills directory and load all skill definitions."""
        with self._lock:
            self._skills_cache.clear()
            for path in self.skills_dir.glob("*.json"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        skill = HermesSkill.from_dict(data)
                        self._skills_cache[skill.name] = skill
                except Exception as e:
                    logger.error(f"Failed to load skill file {path}: {e}")

    def save_skill(self, skill: HermesSkill) -> HermesSkill:
        """Persist a skill to disk in both JSON and SKILL.md representations."""
        with self._lock:
            self._skills_cache[skill.name] = skill
            json_path = self.skills_dir / f"{skill.name}.json"
            md_path = self.skills_dir / f"{skill.name}.md"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(skill.to_dict(), f, indent=2, ensure_ascii=False)

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(skill.to_markdown())

            logger.info(f"Learned and saved new skill: {skill.name}")
            return skill

    def learn_from_experience(
        self,
        name: str,
        description: str,
        trigger_phrases: List[str],
        procedure: List[str],
        prerequisites: Optional[List[str]] = None,
        verification: str = "",
        tags: Optional[List[str]] = None,
    ) -> HermesSkill:
        """
        Extract and commit a new skill learned from an agent turn or problem solution.
        """
        skill = HermesSkill(
            name=name,
            description=description,
            trigger_phrases=trigger_phrases,
            procedure=procedure,
            prerequisites=prerequisites,
            verification=verification,
            tags=tags,
        )
        saved = self.save_skill(skill)

        # Bridge with memory_manager if available
        try:
            from services.memory_manager import memory_manager
            memory_manager.add_memory(
                content=f"Learned Skill [{skill.name}]: {skill.description}. Triggers: {', '.join(skill.trigger_phrases)}",
                category="learned_skill",
                tags=[skill.name] + skill.tags,
            )
        except Exception as e:
            logger.debug(f"Memory manager bridge skipped for skill {skill.name}: {e}")

        return saved

    def get_skill(self, name: str) -> Optional[HermesSkill]:
        """Fetch skill by name."""
        with self._lock:
            clean_name = re.sub(r"[^a-z0-9\-]", "-", name.lower().strip()).strip("-")
            return self._skills_cache.get(clean_name)

    def find_matching_skills(self, user_query: str, limit: int = 3) -> List[HermesSkill]:
        """
        Match incoming query against trigger phrases, skill names, and tags.
        """
        self.load_all_skills()
        query = user_query.lower()
        scored_skills: List[tuple[int, HermesSkill]] = []

        with self._lock:
            for skill in self._skills_cache.values():
                score = 0
                # Exact trigger phrase match
                for trigger in skill.trigger_phrases:
                    if trigger in query:
                        score += 10
                    elif any(word in query for word in trigger.split() if len(word) > 3):
                        score += 3

                # Name match
                name_words = skill.name.replace("-", " ").split()
                if any(w in query for w in name_words if len(w) > 3):
                    score += 5

                # Tag match
                for tag in skill.tags:
                    if tag.lower() in query:
                        score += 2

                if score > 0:
                    scored_skills.append((score, skill))

        scored_skills.sort(key=lambda x: x[0], reverse=True)
        return [skill for _, skill in scored_skills[:limit]]

    def format_skills_for_prompt(self, user_query: str) -> str:
        """
        Build an authoritative skill context block when user query matches learned skills.
        """
        matched = self.find_matching_skills(user_query)
        if not matched:
            return ""

        blocks = []
        for s in matched:
            steps_str = "\n".join([f"    {i+1}. {step}" for i, step in enumerate(s.procedure)])
            blocks.append(
                f"Skill: {s.name}\n"
                f"Description: {s.description}\n"
                f"Procedure:\n{steps_str}\n"
                f"Verification: {s.verification}"
            )

        content = "\n\n".join(blocks)
        return (
            "<skills-context>\n"
            "[System note: The following are learned skills recalled from past experience. "
            "Follow these canonical steps to solve the user's request efficiently.]\n\n"
            f"{content}\n"
            "</skills-context>"
        )

    def list_all_skills(self) -> List[Dict[str, Any]]:
        """List summary of all available skills."""
        with self._lock:
            return [skill.to_dict() for skill in self._skills_cache.values()]


# Global singleton instance
skills_engine = SkillsEngine()
