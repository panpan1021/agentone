import os
from utils.config_handler import rag_config, models_config
from utils.logger_handler import logger


def get_model_by_name(model_name: str | None = None):
    """
    根据模型名称获取对应的 LLM 实例
    如果 model_name 为 None，则使用默认模型
    """
    if model_name is None:
        model_name = models_config.get("default_model", "qwen3-max")

    # 查找模型配置
    model_config = None
    for m in models_config.get("models", []):
        if m["name"] == model_name:
            model_config = m
            break

    if model_config is None:
        logger.warning(f"[model]未找到模型配置: {model_name}，使用默认模型")
        model_name = models_config.get("default_model", "qwen3-max")
        for m in models_config.get("models", []):
            if m["name"] == model_name:
                model_config = m
                break

    provider = model_config["provider"]
    model_id = model_config["model_id"]
    logger.info(f"[model]初始化模型: {model_name} (provider={provider}, model_id={model_id})")

    if provider == "tongyi":
        from langchain_community.chat_models.tongyi import ChatTongyi
        return ChatTongyi(model=model_id)

    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(model=model_id, temperature=0.7)

    elif provider == "openai":
        from langchain_community.chat_models import ChatOpenAI
        return ChatOpenAI(
            model=model_id,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
        )

    else:
        raise ValueError(f"不支持的模型提供商: {provider}")


chat_model = get_model_by_name()
_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from langchain_community.embeddings import DashScopeEmbeddings
        _embedding_model = DashScopeEmbeddings(model=rag_config["embedding_model_name"])
    return _embedding_model
