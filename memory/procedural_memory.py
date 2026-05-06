from __future__ import annotations

from datetime import datetime

from memory.storage import MemoryStorage


class ProceduralMemory:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    def upsert(self, rule_type: str, rule_text: str, priority: int = 5, source: str = "conversation", is_active: int = 1) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        self.storage.execute(
            """
            INSERT INTO procedural_memory (rule_type, rule_text, priority, source, created_at, updated_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(rule_type, rule_text) DO UPDATE SET
                priority = excluded.priority,
                source = excluded.source,
                updated_at = excluded.updated_at,
                is_active = excluded.is_active
            """,
            (rule_type, rule_text, priority, source, now, now, is_active),
        )

    def search(self, query: str, limit: int = 8) -> list[dict]:
        like = f"%{query}%"
        return self.storage.fetch_all(
            """
            SELECT * FROM procedural_memory
            WHERE is_active = 1 AND (rule_type LIKE ? OR rule_text LIKE ?)
            ORDER BY priority DESC, updated_at DESC
            LIMIT ?
            """,
            (like, like, limit),
        )

    def list_active(self, limit: int = 20) -> list[dict]:
        return self.storage.fetch_all(
            "SELECT * FROM procedural_memory WHERE is_active = 1 ORDER BY priority DESC, updated_at DESC LIMIT ?",
            (limit,),
        )
