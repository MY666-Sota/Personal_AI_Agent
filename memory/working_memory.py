from __future__ import annotations

from datetime import datetime

from memory.storage import MemoryStorage


class WorkingMemory:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    def next_turn_id(self, session_id: str) -> int:
        row = self.storage.fetch_one(
            "SELECT MAX(turn_id) AS max_turn FROM working_memory WHERE session_id = ?",
            (session_id,),
        )
        max_turn = row["max_turn"] if row and row["max_turn"] is not None else 0
        return int(max_turn) + 1

    def add(self, session_id: str, role: str, content: str) -> None:
        self.storage.execute(
            "INSERT INTO working_memory (session_id, turn_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                session_id,
                self.next_turn_id(session_id),
                role,
                content,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

    def list_recent(self, session_id: str, limit: int = 10) -> list[dict]:
        rows = self.storage.fetch_all(
            "SELECT session_id, turn_id, role, content, created_at FROM working_memory WHERE session_id = ? ORDER BY turn_id DESC LIMIT ?",
            (session_id, limit),
        )
        return list(reversed(rows))

    def clear_session(self, session_id: str) -> None:
        self.storage.execute("DELETE FROM working_memory WHERE session_id = ?", (session_id,))
