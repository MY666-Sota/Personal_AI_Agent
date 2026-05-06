from __future__ import annotations

from langchain_core.tools import tool

from memory.memory_manager import MemoryManager
from rag.rag_service import RagSummarizeService

rag = RagSummarizeService()
memory = MemoryManager()


@tool
def rag_summarize(query: str) -> str:
    """从个人知识库中检索参考资料，并返回总结结果。"""
    return rag.rag_summarize(query)


@tool
def search_semantic_memory(query: str) -> str:
    """检索长期事实记忆，返回与个人背景、经历、项目和偏好相关的内容。"""
    items = memory.semantic.search(query, limit=5)
    if not items:
        return ""
    return "\n".join([f"{item['category']} / {item['key']}：{item['value']}" for item in items])


@tool
def search_procedural_memory(query: str) -> str:
    """检索长期规则记忆，返回与决策逻辑、写作偏好和工程原则相关的内容。"""
    items = memory.procedural.search(query, limit=5)
    if not items:
        return ""
    return "\n".join([f"{item['rule_type']}：{item['rule_text']}" for item in items])


@tool
def search_episodic_memory(query: str) -> str:
    """检索阶段性经历记忆，返回过去讨论过的主题和总结。"""
    items = memory.episodic.search(query, limit=3)
    if not items:
        return ""
    return "\n".join([f"{item['topic']}：{item['summary']}" for item in items])


@tool
def save_memory_fact(payload: str) -> str:
    """手动写入长期事实记忆。入参格式：category|key|value。"""
    try:
        category, key, value = [part.strip() for part in payload.split("|", 2)]
        memory.semantic.upsert(category=category, key=key, value=value, source="tool")
        return "长期事实记忆已保存"
    except Exception:
        return "写入失败，格式应为：category|key|value"


@tool
def save_memory_rule(payload: str) -> str:
    """手动写入长期规则记忆。入参格式：rule_type|rule_text|priority。"""
    try:
        rule_type, rule_text, priority = [part.strip() for part in payload.split("|", 2)]
        memory.procedural.upsert(rule_type=rule_type, rule_text=rule_text, priority=int(priority), source="tool")
        return "长期规则记忆已保存"
    except Exception:
        return "写入失败，格式应为：rule_type|rule_text|priority"


@tool
def save_memory_episode(payload: str) -> str:
    """手动写入阶段性经历记忆。入参格式：topic|summary。"""
    try:
        topic, summary = [part.strip() for part in payload.split("|", 1)]
        memory.episodic.add(session_id="manual", topic=topic, summary=summary, source="tool")
        return "阶段性经历记忆已保存"
    except Exception:
        return "写入失败，格式应为：topic|summary"
