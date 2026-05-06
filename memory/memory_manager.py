from __future__ import annotations

from memory.episodic_memory import EpisodicMemory
from memory.memory_extractor import MemoryExtractor
from memory.procedural_memory import ProceduralMemory
from memory.semantic_memory import SemanticMemory
from memory.storage import MemoryStorage
from memory.working_memory import WorkingMemory
from utils.logger_handler import logger


class MemoryManager:
    def __init__(self):
        self.storage = MemoryStorage()
        self.working = WorkingMemory(self.storage)
        self.episodic = EpisodicMemory(self.storage)
        self.semantic = SemanticMemory(self.storage)
        self.procedural = ProceduralMemory(self.storage)
        self.extractor = MemoryExtractor()

    def append_conversation(self, session_id: str, role: str, content: str) -> None:
        self.working.add(session_id=session_id, role=role, content=content)

    def search_relevant_memories(self, query: str) -> dict:
        return {
            "semantic": self.semantic.search(query, limit=5),
            "procedural": self.procedural.search(query, limit=5),
            "episodic": self.episodic.search(query, limit=3),
        }

    def load_context_for_query(self, session_id: str, query: str) -> dict:
        return {
            "working": self.working.list_recent(session_id, limit=8),
            **self.search_relevant_memories(query),
        }

    def format_context(self, session_id: str, query: str) -> str:
        context = self.load_context_for_query(session_id, query)
        parts: list[str] = []

        working = context.get("working", [])
        if working:
            lines = [f"[{item['role']}] {item['content']}" for item in working]
            parts.append("【最近对话】\n" + "\n".join(lines))

        semantic = context.get("semantic", [])
        if semantic:
            lines = [f"- {item['category']} / {item['key']}：{item['value']}" for item in semantic]
            parts.append("【长期事实】\n" + "\n".join(lines))

        procedural = context.get("procedural", [])
        if procedural:
            lines = [f"- {item['rule_type']}：{item['rule_text']}" for item in procedural]
            parts.append("【偏好与规则】\n" + "\n".join(lines))

        episodic = context.get("episodic", [])
        if episodic:
            lines = [f"- {item['topic']}：{item['summary']}" for item in episodic]
            parts.append("【相关经历】\n" + "\n".join(lines))

        return "\n\n".join(parts).strip()

    def extract_and_persist(self, session_id: str, user_query: str, assistant_answer: str) -> None:
        result = self.extractor.extract(user_query, assistant_answer)
        for item in result.semantic:
            self.semantic.upsert(
                category=item.category,
                key=item.key,
                value=item.value,
                source="conversation",
                confidence=item.confidence,
            )
        for item in result.procedural:
            self.procedural.upsert(
                rule_type=item.rule_type,
                rule_text=item.rule_text,
                priority=item.priority,
                source="conversation",
            )
        for item in result.episodic:
            self.episodic.add(
                session_id=session_id,
                topic=item.topic,
                summary=item.summary,
                raw_text=item.raw_text,
                source="conversation",
                importance=item.importance,
            )
        logger.info(
            f"[MemoryManager] 写回完成：semantic={len(result.semantic)} procedural={len(result.procedural)} episodic={len(result.episodic)}"
        )
