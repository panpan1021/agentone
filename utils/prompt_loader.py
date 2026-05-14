from utils.config_handler import prompts_config
from utils.path_tool import get_abs_path
from utils.logger_handler import logger

def _load_prompt(config_key: str, error_prefix: str = "") -> str:
    """通用的提示词加载函数"""
    try:
        prompt_path = get_abs_path(prompts_config[config_key])
    except KeyError as e:
        logger.error(f"[{error_prefix}]在配置中没有找到配置项: {config_key}")
        raise e

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"[{error_prefix}]解析提示词文件 {prompt_path} 错误: {str(e)}")
        raise e


def load_system_prompts():
    return _load_prompt("main_prompt_path", "load_system_prompts")


def load_rag_prompts():
    return _load_prompt("rag_summarize_prompt_path", "load_rag_prompts")
def load_report_prompts():
    return _load_prompt("report_prompt_path", "load_report_prompts")
