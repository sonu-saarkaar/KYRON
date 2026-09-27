"""
KYRON Session Manager — ChatGPT/Claude-style Persistent Multi-Session Management.

Features:
1. SQLite-backed persistent chat history across server reloads and restarts.
2. Full multi-session support (create, switch, list, delete, title generation).
3. Thread-safe queries and automatic WAL journaling.
4. Auto title generation from user's first prompt (e.g. "Python Print Asif").
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SessionManager:
    """Persistent Session and Conversation History Manager using SQLite."""

    _instance: Optional[SessionManager] = None
    _init_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super(SessionManager, cls).__new__(cls)
            return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        if db_path is None:
            storage_dir = Path(__file__).resolve().parent.parent / "storage"
            storage_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = storage_dir / "chat_sessions.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._init_database()
        self._initialized = True

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_database(self) -> None:
        """Create tables and indexes if they do not exist."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL DEFAULT 'default_user',
                        title TEXT NOT NULL DEFAULT 'New Conversation',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        metadata TEXT DEFAULT '{}'
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        sender TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        metadata TEXT DEFAULT '{}',
                        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id, updated_at DESC);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, created_at ASC);")
                conn.commit()

    @staticmethod
    def generate_smart_title(first_prompt: str) -> str:
        """Generate a clean, readable ChatGPT-style session title from the first prompt."""
        if not first_prompt:
            return "New Conversation"

        clean = first_prompt.strip()
        # Remove common greetings or filler words
        clean = re.sub(r"^(hey|hi|hello|namaste|sun|bhai|boss|kya|aap)\s+", "", clean, flags=re.IGNORECASE)
        # Take first line if multiple
        clean = clean.split("\n")[0].strip()
        # Remove trailing punctuation
        clean = clean.rstrip("?.!:,;")
        if len(clean) > 40:
            clean = clean[:37] + "..."
        if not clean:
            return "New Conversation"
        return clean[:1].upper() + clean[1:]

    def create_session(
        self,
        user_id: str = "default_user",
        title: str = "New Conversation",
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new chat session."""
        now = datetime.now().isoformat()
        sid = session_id or f"sess_{uuid.uuid4().hex[:12]}"
        meta_str = json.dumps(metadata or {})

        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO sessions (id, user_id, title, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                    (sid, user_id, title, now, now, meta_str)
                )
                conn.commit()

        return {
            "id": sid,
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "metadata": metadata or {},
            "messages": []
        }

    def get_or_create_session(self, session_id: Optional[str] = None, user_id: str = "default_user") -> Dict[str, Any]:
        """Retrieve existing session or create a new one if not found."""
        if session_id:
            sess = self.get_session(session_id)
            if sess:
                return sess
        return self.create_session(user_id=user_id, session_id=session_id)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata and all its messages."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
                row = cur.fetchone()
                if not row:
                    return None

                session_dict = dict(row)
                try:
                    session_dict["metadata"] = json.loads(session_dict.get("metadata") or "{}")
                except Exception:
                    session_dict["metadata"] = {}

                # Get messages
                mcur = conn.execute(
                    "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                    (session_id,)
                )
                messages = []
                for mrow in mcur.fetchall():
                    m = dict(mrow)
                    try:
                        m["metadata"] = json.loads(m.get("metadata") or "{}")
                    except Exception:
                        m["metadata"] = {}
                    messages.append(m)

                session_dict["messages"] = messages
                return session_dict

    def list_sessions(self, user_id: str = "default_user", limit: int = 50) -> List[Dict[str, Any]]:
        """List all chat sessions for user ordered by recent activity."""
        with self._lock:
            with self._get_connection() as conn:
                query = """
                    SELECT 
                        s.*,
                        COUNT(m.id) as message_count,
                        (SELECT content FROM messages WHERE session_id = s.id ORDER BY created_at DESC LIMIT 1) as last_message
                    FROM sessions s
                    LEFT JOIN messages m ON s.id = m.session_id
                    WHERE s.user_id = ?
                    GROUP BY s.id
                    ORDER BY s.updated_at DESC
                    LIMIT ?
                """
                cur = conn.execute(query, (user_id, limit))
                results = []
                for row in cur.fetchall():
                    item = dict(row)
                    try:
                        item["metadata"] = json.loads(item.get("metadata") or "{}")
                    except Exception:
                        item["metadata"] = {}
                    results.append(item)
                return results

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sender: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a message to a session and update session's updated_at / title."""
        if not sender:
            sender = "user" if role == "user" else "kyron"

        now = datetime.now().isoformat()
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        meta_str = json.dumps(metadata or {})

        with self._lock:
            with self._get_connection() as conn:
                # Ensure session exists
                cur = conn.execute("SELECT id, title FROM sessions WHERE id = ?", (session_id,))
                sess = cur.fetchone()
                if not sess:
                    title = self.generate_smart_title(content) if role == "user" else "New Conversation"
                    conn.execute(
                        "INSERT INTO sessions (id, user_id, title, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                        (session_id, "default_user", title, now, now, "{}")
                    )
                else:
                    # Update title if still default and this is first user message
                    current_title = sess["title"]
                    if (current_title == "New Conversation" or not current_title) and role == "user":
                        new_title = self.generate_smart_title(content)
                        conn.execute("UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?", (new_title, now, session_id))
                    else:
                        conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))

                conn.execute(
                    "INSERT INTO messages (id, session_id, role, sender, content, created_at, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (msg_id, session_id, role, sender, content, now, meta_str)
                )
                conn.commit()

        return {
            "id": msg_id,
            "session_id": session_id,
            "role": role,
            "sender": sender,
            "content": content,
            "created_at": now,
            "metadata": metadata or {}
        }

    def get_recent_history_for_llm(self, session_id: str, limit: int = 15) -> List[Dict[str, str]]:
        """
        Fetch recent messages formatted for OpenAI / Hermes LLM messages payload:
        [{"role": "user"|"assistant", "content": "..."}]
        """
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT role, content FROM (
                        SELECT role, content, created_at FROM messages
                        WHERE session_id = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    ) ORDER BY created_at ASC
                    """,
                    (session_id, limit)
                )
                formatted = []
                for row in cur.fetchall():
                    role = "assistant" if row["role"] in ("assistant", "bot", "kyron") else "user"
                    formatted.append({"role": role, "content": row["content"]})
                return formatted

    def update_session_title(self, session_id: str, new_title: str) -> bool:
        """Update session title."""
        now = datetime.now().isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                    (new_title.strip() or "New Conversation", now, session_id)
                )
                conn.commit()
                return cur.rowcount > 0

    def delete_session(self, session_id: str) -> bool:
        """Delete session and all its messages."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                conn.commit()
                return cur.rowcount > 0

    def clear_all_sessions(self, user_id: str = "default_user") -> bool:
        """Delete all sessions for a user."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
                conn.commit()
                return True


# Global Singleton Instance
session_manager = SessionManager()
