import os
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Optional

from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings

from utils.config_handler import rag_conf


def _require_dashscope_api_key() -> None:
    if not os.getenv("DASHSCOPE_API_KEY"):
        raise EnvironmentError("未检测到 DASHSCOPE_API_KEY，请先在环境变量中完成配置。")


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        raise NotImplementedError


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        _require_dashscope_api_key()
        return ChatTongyi(model=rag_conf["chat_model_name"])


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        _require_dashscope_api_key()
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])


@lru_cache(maxsize=1)
def get_chat_model() -> BaseChatModel:
    model = ChatModelFactory().generator()
    if model is None:
        raise RuntimeError("对话模型初始化失败。")
    return model


@lru_cache(maxsize=1)
def get_embed_model() -> Embeddings:
    model = EmbeddingsFactory().generator()
    if model is None:
        raise RuntimeError("向量模型初始化失败。")
    return model
