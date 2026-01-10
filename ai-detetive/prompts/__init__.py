"""
提示词管理模块
用于集中管理各个Agent的提示词
"""

from pathlib import Path

# 定义提示词文件路径
PROMPTS_DIR = Path(__file__).parent


def load_prompt(prompt_name: str) -> str:
    """
    加载提示词文件
    
    Args:
        prompt_name: 提示词文件名（不含.txt后缀）
        
    Returns:
        提示词内容
    """
    prompt_file = PROMPTS_DIR / f"{prompt_name}_prompt.txt"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


# 提示词名称常量
CODE_AGENT = "code_agent"
COORDINATOR_AGENT = "coordinator_agent"
DB_AGENT = "db_agent"
DLD_AGENT = "dld_agent"
LOG_AGENT = "log_agent"
PRD_AGENT = "prd_agent"


def get_code_agent_prompt() -> str:
    """获取代码Agent的提示词"""
    return load_prompt(CODE_AGENT)


def get_coordinator_agent_prompt() -> str:
    """获取协调者Agent的提示词"""
    return load_prompt(COORDINATOR_AGENT)


def get_db_agent_prompt() -> str:
    """获取数据库Agent的提示词"""
    return load_prompt(DB_AGENT)


def get_dld_agent_prompt() -> str:
    """获取业务流程Agent的提示词"""
    return load_prompt(DLD_AGENT)


def get_log_agent_prompt() -> str:
    """获取日志Agent的提示词"""
    return load_prompt(LOG_AGENT)


def get_prd_agent_prompt() -> str:
    """获取产品需求Agent的提示词"""
    return load_prompt(PRD_AGENT)


__all__ = [
    "load_prompt",
    "CODE_AGENT",
    "COORDINATOR_AGENT",
    "DB_AGENT",
    "DLD_AGENT",
    "LOG_AGENT",
    "PRD_AGENT",
    "get_code_agent_prompt",
    "get_coordinator_agent_prompt",
    "get_db_agent_prompt",
    "get_dld_agent_prompt",
    "get_log_agent_prompt",
    "get_prd_agent_prompt"
]
