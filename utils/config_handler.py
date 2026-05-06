import yaml

from utils.path_tool import get_abs_path


def _load_yaml_config(config_path: str, encoding: str = "utf-8") -> dict:
    with open(config_path, "r", encoding=encoding) as file:
        return yaml.safe_load(file) or {}


def load_rag_config(config_path: str = get_abs_path("config/rag.yml"), encoding: str = "utf-8") -> dict:
    return _load_yaml_config(config_path, encoding)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml"), encoding: str = "utf-8") -> dict:
    return _load_yaml_config(config_path, encoding)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml"), encoding: str = "utf-8") -> dict:
    return _load_yaml_config(config_path, encoding)


rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
