from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class MemoryStorage:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or get_abs_path("runtime/memory.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS working_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    turn_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS episodic_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    topic TEXT,
                    summary TEXT NOT NULL,
                    raw_text TEXT,
                    source TEXT,
                    importance REAL DEFAULT 0.5,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    source TEXT,
                    confidence REAL DEFAULT 0.8,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(category, key)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS procedural_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_type TEXT NOT NULL,
                    rule_text TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    source TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    UNIQUE(rule_type, rule_text)
                )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_working_session ON working_memory(session_id, turn_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_episodic_topic ON episodic_memory(topic, created_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_semantic_category_key ON semantic_memory(category, key)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_procedural_type_active ON procedural_memory(rule_type, is_active)")
            logger.info("[MemoryStorage] memory.db 初始化完成")

    def execute(self, sql: str, params: Iterable[Any] = ()) -> None:
        with self.get_conn() as conn:
            conn.execute(sql, tuple(params))

    def execute_many(self, sql: str, params: list[tuple[Any, ...]]) -> None:
        with self.get_conn() as conn:
            conn.executemany(sql, params)

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
        with self.get_conn() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
            return [dict(row) for row in rows]

    def fetch_one(self, sql: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
        with self.get_conn() as conn:
            row = conn.execute(sql, tuple(params)).fetchone()
            return dict(row) if row else None
