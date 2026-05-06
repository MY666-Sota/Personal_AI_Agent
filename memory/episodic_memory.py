from __future__ import annotations

from datetime import datetime

from memory.storage import MemoryStorage


class EpisodicMemory:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    def add(self, session_id: str, topic: str, summary: str, raw_text: str = "", source: str = "conversation", importance: float = 0.5):
        self.storage.execute(
            "INSERT INTO episodic_memory (session_id, topic, summary, raw_text, source, importance, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, topic, summary, raw_text, source, importance, datetime.now().isoformat(timespec="seconds")),
        )

    def search(self, query: str, limit: int = 5) -> list[dict]:
        like = f"%{query}%"
        return self.storage.fetch_all(
            """
            SELECT * FROM episodic_memory
            WHERE topic LIKE ? OR summary LIKE ? OR raw_text LIKE ?
            ORDER BY importance DESC, created_at DESC
            LIMIT ?
            """,
            (like, like, like, limit),
        )

    def list_recent(self, limit: int = 10) -> list[dict]:
        return self.storage.fetch_all(
            "SELECT * FROM episodic_memory ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
