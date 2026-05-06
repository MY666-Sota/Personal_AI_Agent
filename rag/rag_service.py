"""
总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复。
"""
from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from model.factory import get_chat_model
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts


class RagSummarizeService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.vector_store.load_document()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = get_chat_model()
        self.chain = self._init_chain()

    def _init_chain(self):
        return self.prompt_template | self.model | StrOutputParser()

    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)
        if not context_docs:
            return "当前资料库中没有检索到与该问题直接相关的内容。"

        context_parts: list[str] = []
        for idx, doc in enumerate(context_docs, start=1):
            context_parts.append(f"【参考资料{idx}】\n内容：{doc.page_content}\n元数据：{doc.metadata}")

        return self.chain.invoke({"input": query, "context": "\n\n".join(context_parts)})
