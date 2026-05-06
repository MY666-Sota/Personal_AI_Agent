from __future__ import annotations

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from model.factory import get_embed_model
from utils.config_handler import chroma_conf
from utils.file_handler import (
    get_file_md5_hex,
    listdir_with_allowed_type,
    md_loader,
    pdf_loader,
    txt_loader,
)
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class VectorStoreService:
    def __init__(self):
        self.persist_directory = self._resolve_path(chroma_conf["persist_directory"])
        self.data_path = self._resolve_path(chroma_conf["data_path"])
        self.md5_store_path = self._resolve_path(chroma_conf["md5_hex_store"])

        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        Path(self.md5_store_path).parent.mkdir(parents=True, exist_ok=True)

        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=get_embed_model(),
            persist_directory=self.persist_directory,
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    @staticmethod
    def _resolve_path(path: str) -> str:
        return path if os.path.isabs(path) else get_abs_path(path)

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def _get_category_from_path(self, read_path: str) -> str:
        parts = Path(read_path).parts
        categories = {"profile", "learning", "work", "projects", "decision_logic", "preferences"}
        for part in parts:
            if part in categories:
                return part
        return "general"

    def _load_documents(self, read_path: str) -> list[Document]:
        if read_path.endswith(".txt"):
            docs = txt_loader(read_path)
        elif read_path.endswith(".md"):
            docs = md_loader(read_path)
        elif read_path.endswith(".pdf"):
            docs = pdf_loader(read_path)
        else:
            return []

        category = self._get_category_from_path(read_path)
        filename = os.path.basename(read_path)
        for doc in docs:
            doc.metadata = {**doc.metadata, "category": category, "source_file": filename, "source_path": read_path}
        return docs

    def load_document(self):
        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(self.md5_store_path):
                open(self.md5_store_path, "w", encoding="utf-8").close()
                return False
            with open(self.md5_store_path, "r", encoding="utf-8") as file:
                return any(line.strip() == md5_for_check for line in file.readlines())

        def save_md5_hex(md5_for_check: str):
            with open(self.md5_store_path, "a", encoding="utf-8") as file:
                file.write(md5_for_check + "\n")

        if not os.path.isdir(self.data_path):
            logger.warning(f"[加载知识库] 未找到资料目录：{self.data_path}")
            return

        allowed_files_path = listdir_with_allowed_type(
            self.data_path,
            tuple(f".{file_type.lstrip('.')}" for file_type in chroma_conf["allow_knowledge_file_type"]),
        )

        for path in allowed_files_path:
            md5_hex = get_file_md5_hex(path)
            if md5_hex and check_md5_hex(md5_hex):
                logger.info(f"[加载知识库] {path} 已存在于向量库中，跳过。")
                continue

            try:
                documents = self._load_documents(path)
                if not documents:
                    logger.warning(f"[加载知识库] {path} 中没有可用文本内容，跳过。")
                    continue
                split_documents = self.spliter.split_documents(documents)
                if not split_documents:
                    logger.warning(f"[加载知识库] {path} 切分后没有可用文本内容，跳过。")
                    continue
                self.vector_store.add_documents(split_documents)
                if md5_hex:
                    save_md5_hex(md5_hex)
                logger.info(f"[加载知识库] {path} 入库完成。")
            except Exception as exc:
                logger.error(f"[加载知识库] {path} 加载失败：{exc}", exc_info=True)
