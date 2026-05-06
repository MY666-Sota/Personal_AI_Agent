from __future__ import annotations

from datetime import datetime

from memory.storage import MemoryStorage


class SemanticMemory:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    def upsert(self, category: str, key: str, value: str, source: str = "conversation", confidence: float = 0.8) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        self.storage.execute(
            """
            INSERT INTO semantic_memory (category, key, value, source, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(category, key) DO UPDATE SET
                value = excluded.value,
                source = excluded.source,
                confidence = excluded.confidence,
                updated_at = excluded.updated_at
            """,
            (category, key, value, source, confidence, now, now),
        )

    def search(self, query: str, limit: int = 8) -> list[dict]:
        like = f"%{query}%"
        return self.storage.fetch_all(
            """
            SELECT * FROM semantic_memory
            WHERE category LIKE ? OR key LIKE ? OR value LIKE ?
            ORDER BY updated_at DESC, confidence DESC
            LIMIT ?
            """,
            (like, like, like, limit),
        )

    def list_by_category(self, category: str, limit: int = 20) -> list[dict]:
        return self.storage.fetch_all(
            "SELECT * FROM semantic_memory WHERE category = ? ORDER BY updated_at DESC LIMIT ?",
            (category, limit),
        )
