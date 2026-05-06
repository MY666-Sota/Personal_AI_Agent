from utils.config_handler import prompts_conf
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


def load_system_prompts() -> str:
    try:
        system_prompt_path = get_abs_path(prompts_conf["main_prompt_path"])
    except KeyError as exc:
        logger.error("[load_system_prompts] 在 yaml 配置项中没有 main_prompt_path 配置项")
        raise exc

    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as exc:
        logger.error(f"[load_system_prompts] 解析系统提示词出错：{exc}")
        raise exc


def load_rag_prompts() -> str:
    try:
        rag_prompt_path = get_abs_path(prompts_conf["rag_summarize_prompt_path"])
    except KeyError as exc:
        logger.error("[load_rag_prompts] 在 yaml 配置项中没有 rag_summarize_prompt_path 配置项")
        raise exc

    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()
    except Exception as exc:
        logger.error(f"[load_rag_prompts] 解析 RAG 提示词出错：{exc}")
        raise exc
