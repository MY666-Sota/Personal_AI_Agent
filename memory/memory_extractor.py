from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from memory.schemas import (
    EpisodicMemoryItem,
    MemoryExtractionResult,
    ProceduralMemoryItem,
    SemanticMemoryItem,
)
from model.factory import get_chat_model
from utils.logger_handler import logger


EXTRACTION_PROMPT = """
你是一个“长期记忆抽取器”。请根据用户问题和助手回答，只抽取对未来持续有价值的信息，并输出 JSON。

抽取规则：
1. 只抽取长期稳定事实、稳定偏好、反复适用的决策规则、值得保留的阶段性事件。
2. 一次性临时信息、情绪性表达、没有把握的推断，不要抽取。
3. 如果没有可抽取内容，对应数组返回空数组。
4. 只输出 JSON，不要输出解释。

JSON 格式：
{{
  "semantic": [
    {{"category": "projects", "key": "current_project", "value": "正在开发个人智能助理", "confidence": 0.9}}
  ],
  "procedural": [
    {{"rule_type": "engineering_principle", "rule_text": "优先构建最小可运行闭环，再逐步扩展", "priority": 8}}
  ],
  "episodic": [
    {{"topic": "agent_upgrade", "summary": "决定先开发四层记忆系统", "importance": 0.7}}
  ]
}}

用户问题：{query}
助手回答：{answer}
"""


class MemoryExtractor:
    def __init__(self):
        self.chain = PromptTemplate.from_template(EXTRACTION_PROMPT) | get_chat_model() | StrOutputParser()

    def _extract_json(self, text: str) -> dict[str, Any]:
        text = text.strip()
        fenced = re.search(r"```json\s*(\{.*\})\s*```", text, re.DOTALL)
        if fenced:
            text = fenced.group(1)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise

    def extract(self, query: str, answer: str) -> MemoryExtractionResult:
        try:
            raw = self.chain.invoke({"query": query, "answer": answer})
            data = self._extract_json(raw)
        except Exception as e:
            logger.warning(f"[MemoryExtractor] 抽取失败，跳过本轮写回：{str(e)}")
            return MemoryExtractionResult(raw_response="")

        result = MemoryExtractionResult(raw_response=raw)
        for item in data.get("semantic", []):
            if item.get("category") and item.get("key") and item.get("value"):
                result.semantic.append(
                    SemanticMemoryItem(
                        category=item["category"],
                        key=item["key"],
                        value=item["value"],
                        confidence=float(item.get("confidence", 0.8)),
                    )
                )

        for item in data.get("procedural", []):
            if item.get("rule_type") and item.get("rule_text"):
                result.procedural.append(
                    ProceduralMemoryItem(
                        rule_type=item["rule_type"],
                        rule_text=item["rule_text"],
                        priority=int(item.get("priority", 5)),
                    )
                )

        for item in data.get("episodic", []):
            if item.get("topic") and item.get("summary"):
                result.episodic.append(
                    EpisodicMemoryItem(
                        session_id="",
                        topic=item["topic"],
                        summary=item["summary"],
                        raw_text=f"用户问题：{query}\n助手回答：{answer}",
                        importance=float(item.get("importance", 0.5)),
                    )
                )
        return result
