import yaml
from functools import lru_cache
from utils.path_tool import get_abs_path


@lru_cache(maxsize=4)
def _load_yaml_config(config_path: str, encoding: str = "utf-8"):
    """通用的YAML配置文件加载函数，带缓存"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_rag_config():
    return _load_yaml_config(get_abs_path("config/rag.yml"))


def load_chroma_config():
    return _load_yaml_config(get_abs_path("config/chroma.yml"))


def load_prompt_config():
    return _load_yaml_config(get_abs_path("config/prompt.yml"))


def load_agent_config():
    return _load_yaml_config(get_abs_path("config/agent.yml"))


def load_models_config():
    return _load_yaml_config(get_abs_path("config/models.yml"))


rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompt_config()
agent_config = load_agent_config()
models_config = load_models_config()
