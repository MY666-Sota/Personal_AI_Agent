from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from memory.memory_manager import MemoryManager
from model.factory import get_chat_model
from rag.rag_service import RagSummarizeService
from utils.prompt_loader import load_system_prompts


class ReactAgent:
    def __init__(self):
        self.memory = MemoryManager()
        self.system_prompt = load_system_prompts()
        self.model = get_chat_model()
        self.rag_service = RagSummarizeService()

    def _build_messages(self, session_id: str, query: str):
        memory_context = self.memory.format_context(session_id=session_id, query=query)
        rag_context = self.rag_service.rag_summarize(query)

        user_parts = []
        if memory_context:
            user_parts.append(f"以下是与当前问题相关的长期记忆和近期对话：\n{memory_context}")
        if rag_context:
            user_parts.append(f"以下是从资料库中整理出的参考信息：\n{rag_context}")
        user_parts.append(f"当前用户问题：\n{query}")

        return [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content="\n\n".join(user_parts)),
        ]

    def execute_stream(self, query: str, session_id: str = "default"):
        self.memory.append_conversation(session_id, "user", query)

        try:
            response = self.model.invoke(self._build_messages(session_id, query))
            final_answer = getattr(response, "content", str(response)).strip()
        except Exception as exc:
            final_answer = f"当前请求执行失败：{exc}"

        if final_answer:
            self.memory.append_conversation(session_id, "assistant", final_answer)
            self.memory.extract_and_persist(session_id, query, final_answer)
            yield final_answer


if __name__ == "__main__":
    agent = ReactAgent()
    for chunk in agent.execute_stream("根据我的资料，给我一个当前项目推进建议"):
        print(chunk, end="", flush=True)
