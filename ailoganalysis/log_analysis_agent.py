"""
基于 SelectDB JSON 格式日志和 GitLab 代码的问题排查 Agent
"""

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.agents import create_agent
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess
import os


# ==================== 预留的输入数据接口 ====================

# SelectDB JSON 格式日志 (预留输入)
SELECTDB_LOGS = [
    # 示例日志格式，实际使用时替换为真实数据
    # {
    #     "timestamp": "2026-01-04 10:30:45",
    #     "level": "ERROR",
    #     "service": "payment-service",
    #     "message": "Database connection timeout",
    #     "exception": "psycopg2.OperationalError: server closed the connection unexpectedly",
    #     "request_id": "req_12345",
    #     "user_id": "user_67890",
    #     "trace_id": "trace_abc123",
    #     "context": {
    #         "query": "SELECT * FROM orders WHERE status='pending'",
    #         "duration_ms": 5000
    #     }
    # }
]

# GitLab 仓库信息 (预留输入)
GITLAB_CONFIG = {
    "repo_url": "git@your-gitlab.com:your-org/your-repo.git",
    "branch": "main",
    "ssh_key_path": "~/.ssh/id_rsa",
    "local_clone_path": "./temp_code_repo"
}

# 需要分析的代码文件列表 (预留输入)
TARGET_FILES = [
    # "services/payment/service.py",
    # "models/database.py",
    # "api/routes/payment.py"
]


# ==================== 工具函数 ====================

def parse_selectdb_logs(logs: List[Dict]) -> Dict[str, Any]:
    """
    解析 SelectDB JSON 格式日志
    
    Args:
        logs: SelectDB 日志列表
        
    Returns:
        解析后的日志统计信息
    """
    log_stats = {
        "total_logs": len(logs),
        "error_logs": [],
        "warning_logs": [],
        "error_count": 0,
        "warning_count": 0,
        "unique_errors": set(),
        "services": set(),
        "time_range": None
    }
    
    timestamps = []
    
    for log in logs:
        level = log.get("level", "").upper()
        service = log.get("service", "")
        timestamp = log.get("timestamp", "")
        
        if timestamp:
            timestamps.append(timestamp)
        
        if service:
            log_stats["services"].add(service)
        
        if level == "ERROR":
            log_stats["error_count"] += 1
            log_stats["error_logs"].append(log)
            error_msg = log.get("message", "")
            exception = log.get("exception", "")
            log_stats["unique_errors"].add(f"{error_msg} - {exception}")
        
        elif level == "WARNING":
            log_stats["warning_count"] += 1
            log_stats["warning_logs"].append(log)
    
    # 计算时间范围
    if timestamps:
        timestamps.sort()
        log_stats["time_range"] = {
            "start": timestamps[0],
            "end": timestamps[-1]
        }
    
    log_stats["unique_errors"] = list(log_stats["unique_errors"])
    log_stats["services"] = list(log_stats["services"])
    
    return log_stats


def clone_gitlab_repo(gitlab_config: Dict, target_files: Optional[List[str]] = None) -> Dict[str, str]:
    """
    通过 SSH 克隆 GitLab 仓库并获取代码
    
    Args:
        gitlab_config: GitLab 配置信息
        target_files: 需要获取的特定文件列表
        
    Returns:
        文件名到代码内容的映射字典
    """
    repo_url = gitlab_config["repo_url"]
    local_path = gitlab_config["local_clone_path"]
    branch = gitlab_config.get("branch", "main")
    
    # 克隆仓库
    try:
        if os.path.exists(local_path):
            # 如果已存在，则拉取最新代码
            print(f"更新仓库: {local_path}")
            subprocess.run(
                ["git", "-C", local_path, "pull", "origin", branch],
                check=True,
                capture_output=True,
                text=True
            )
        else:
            # 克隆新仓库
            print(f"克隆仓库: {repo_url} 到 {local_path}")
            subprocess.run(
                ["git", "clone", "-b", branch, repo_url, local_path],
                check=True,
                capture_output=True,
                text=True
            )
    except subprocess.CalledProcessError as e:
        print(f"Git 操作失败: {e.stderr}")
        return {}
    
    # 读取文件内容
    code_files = {}
    if target_files:
        for file_path in target_files:
            full_path = os.path.join(local_path, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        code_files[file_path] = f.read()
                except Exception as e:
                    print(f"读取文件 {file_path} 失败: {e}")
            else:
                print(f"文件不存在: {full_path}")
    else:
        # 读取所有 Python 文件
        for root, dirs, files in os.walk(local_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, local_path)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code_files[rel_path] = f.read()
                    except Exception as e:
                        print(f"读取文件 {file_path} 失败: {e}")
    
    return code_files


def extract_key_logs(logs: List[Dict], keywords: List[str] = None) -> List[Dict]:
    """
    提取关键日志
    
    Args:
        logs: 日志列表
        keywords: 关键词列表
        
    Returns:
        关键日志列表
    """
    if keywords is None:
        keywords = ["ERROR", "FATAL", "Exception", "timeout", "failed", "crash"]
    
    key_logs = []
    
    for log in logs:
        log_str = json.dumps(log, ensure_ascii=False).lower()
        for keyword in keywords:
            if keyword.lower() in log_str:
                key_logs.append(log)
                break
    
    return key_logs


def extract_relevant_code(code_files: Dict[str, str], error_keywords: List[str]) -> Dict[str, str]:
    """
    根据错误关键词提取相关代码片段
    
    Args:
        code_files: 代码文件字典
        error_keywords: 错误关键词列表
        
    Returns:
        相关代码片段字典
    """
    relevant_code = {}
    
    for file_path, code in code_files.items():
        lines = code.split('\n')
        relevant_lines = []
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            for keyword in error_keywords:
                if keyword.lower() in line_lower:
                    # 获取前后 5 行上下文
                    start = max(0, i - 6)
                    end = min(len(lines), i + 5)
                    context = lines[start:end]
                    context_with_numbers = [
                        f"{start + j + 1}: {context[j]}" 
                        for j in range(len(context))
                    ]
                    relevant_lines.extend([
                        f"\n--- {file_path}:{i} 关键词 '{keyword}' ---\n",
                        *context_with_numbers,
                        "\n"
                    ])
                    break
        
        if relevant_lines:
            relevant_code[file_path] = ''.join(relevant_lines)
    
    return relevant_code


# ==================== LangChain Agent 工具 ====================

@tool
def analyze_logs(logs: List[Dict]) -> str:
    """
    分析 SelectDB JSON 格式日志，提取错误信息和关键事件
    
    Args:
        logs: SelectDB JSON 格式日志列表
        
    Returns:
        日志分析结果摘要
    """
    stats = parse_selectdb_logs(logs)
    
    result = f"""
=== 日志分析结果 ===
总日志数: {stats['total_logs']}
错误日志数: {stats['error_count']}
警告日志数: {stats['warning_count']}
涉及服务: {', '.join(stats['services'])}
时间范围: {stats['time_range']['start'] if stats['time_range'] else 'N/A'} ~ {stats['time_range']['end'] if stats['time_range'] else 'N/A'}

唯一错误类型:
"""
    for i, error in enumerate(stats['unique_errors'], 1):
        result += f"{i}. {error}\n"
    
    return result


@tool
def search_code(code_files: Dict[str, str], search_term: str) -> str:
    """
    在代码库中搜索特定关键词或函数
    
    Args:
        code_files: 代码文件字典（文件名: 代码内容）
        search_term: 搜索词
        
    Returns:
        搜索结果
    """
    results = []
    
    for file_path, code in code_files.items():
        if search_term.lower() in code.lower():
            lines = code.split('\n')
            matches = []
            for i, line in enumerate(lines, 1):
                if search_term.lower() in line.lower():
                    matches.append(f"  行 {i}: {line.strip()}")
            
            if matches:
                results.append(f"\n文件: {file_path}\n" + '\n'.join(matches))
    
    if results:
        return f"在以下文件中找到 '{search_term}':\n" + '\n'.join(results)
    else:
        return f"未在代码库中找到 '{search_term}'"


@tool  
def get_function_context(code_files: Dict[str, str], function_name: str) -> str:
    """
    获取特定函数的上下文代码
    
    Args:
        code_files: 代码文件字典
        function_name: 函数名
        
    Returns:
        函数代码及上下文
    """
    for file_path, code in code_files.items():
        # 简单的函数名匹配
        pattern = rf'def {re.escape(function_name)}\s*\(|class {re.escape(function_name)}\s*\(|async def {re.escape(function_name)}\s*\('
        matches = list(re.finditer(pattern, code))
        
        if matches:
            lines = code.split('\n')
            contexts = []
            
            for match in matches:
                start_line = code[:match.start()].count('\n')
                # 获取函数或类定义后的 30 行
                end_line = min(len(lines), start_line + 30)
                context = '\n'.join(f"{i+1}: {line}" for i, line in enumerate(lines[start_line:end_line], start_line))
                contexts.append(f"\n--- {file_path} ---\n{context}")
            
            return '\n'.join(contexts)
    
    return f"未找到函数或类 '{function_name}'"


@tool
def correlate_log_with_code(logs: List[Dict], code_files: Dict[str, str]) -> str:
    """
    关联日志错误与代码实现
    
    Args:
        logs: 日志列表
        code_files: 代码文件字典
        
    Returns:
        日志与代码的关联分析
    """
    error_logs = [log for log in logs if log.get("level") == "ERROR"]
    
    correlations = []
    
    for log in error_logs:
        message = log.get("message", "")
        exception = log.get("exception", "")
        service = log.get("service", "")
        
        # 提取可能的函数名和关键词
        error_keywords = []
        
        # 从异常中提取类名
        if exception:
            exception_match = re.search(r'(\w+Error|\w+Exception)', exception)
            if exception_match:
                error_keywords.append(exception_match.group(1))
        
        # 从消息中提取关键词
        words = re.findall(r'\b\w+\b', message)
        error_keywords.extend(words[:5])  # 取前5个词
        
        # 搜索相关代码
        relevant_code = extract_relevant_code(code_files, error_keywords)
        
        correlation = f"\n=== 错误: {message} ===\n"
        correlation += f"服务: {service}\n"
        correlation += f"异常: {exception}\n"
        correlation += f"可能的关键词: {', '.join(error_keywords[:5])}\n"
        
        if relevant_code:
            correlation += "\n相关代码片段:\n"
            for file_path, code_snippet in relevant_code.items():
                correlation += f"\n--- {file_path} ---\n{code_snippet[:500]}...\n"
        else:
            correlation += "\n未找到明显相关的代码片段\n"
        
        correlations.append(correlation)
    
    return '\n'.join(correlations)


# ==================== 主 Agent 类 ====================

class LogAnalysisAgent:
    """日志和代码分析 Agent"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1", model: str = "deepseek-chat"):
        """
        初始化 Agent
        
        Args:
            api_key: DeepSeek API Key
            base_url: API base URL
            model: 模型名称
        """
        # 使用 DeepSeek (能力最强的开源模型之一)
        self.llm = init_chat_model(
            model=model,
            model_provider="openai",
            api_key=api_key,
            base_url=base_url,
            temperature=0,  # 使用低温度以获得更确定性的分析
        )
        
        # 定义工具
        self.tools = [
            analyze_logs,
            search_code,
            get_function_context,
            correlate_log_with_code
        ]
        
        # 创建 Agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            debug=False,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的系统问题排查专家，擅长通过分析系统日志和代码来诊断问题。

你的任务是分析 SelectDB JSON 格式的系统日志和 GitLab 代码库，找出问题的根本原因。

请按照以下格式输出分析结果：

---
【置信度】: 0-100之间的整数，表示你对问题原因的确定程度

【问题原因】: 简洁准确地描述问题的根本原因

【问题排查思路】:
1. 步骤一: 描述排查步骤
2. 步骤二: 描述排查步骤
...

【问题原因对应的证据】:
- 证据1: 具体说明
- 证据2: 具体说明
...

【关键日志】:
```json
{
  "timestamp": "...",
  "level": "ERROR",
  "message": "...",
  ...
}
```

【关键代码】:
```python
# 文件路径
# 行号: 代码
```

---

分析原则：
1. 首先分析日志，找出所有错误和异常
2. 然后在代码库中搜索相关的函数和类
3. 关联日志错误和代码实现
4. 根据证据给出最可能的问题原因
5. 提供清晰的排查思路
6. 置信度要客观，证据充分时给高分，证据不足时给低分
"""
    
    def analyze(self, logs: List[Dict], code_files: Dict[str, str]) -> str:
        """
        分析日志和代码
        
        Args:
            logs: SelectDB JSON 格式日志列表
            code_files: 代码文件字典（文件名: 代码内容）
            
        Returns:
            格式化的分析结果
        """
        # 准备输入
        user_message = f"""
请分析以下系统日志和代码，找出问题原因并按照指定格式输出结果。

== 系统日志 (共 {len(logs)} 条) ==
{json.dumps(logs, ensure_ascii=False, indent=2)[:5000]}

== 代码文件 (共 {len(code_files)} 个) ==
"""
        for file_path, code in code_files.items():
            user_message += f"\n=== {file_path} ===\n{code[:3000]}\n"
        
        # 调用 Agent
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            streaming=False
        )
        
        return result.get("messages")[-1].content


# ==================== 主函数示例 ====================

def main():
    """
    主函数示例
    """
    # API Key (请替换为实际的 API Key)
    API_KEY = "sk-94ac4e052ab5486ead278f6bff21db91"
    
    # 初始化 Agent
    agent = LogAnalysisAgent(api_key=API_KEY)
    
    # ==================== 方式1: 使用预留的日志和代码 ====================
    # 如果已设置 SELECTDB_LOGS 和 code_files，直接使用
    if SELECTDB_LOGS:
        print("=== 从 GitLab 克隆代码... ===")
        code_files = clone_gitlab_repo(GITLAB_CONFIG, TARGET_FILES)
        
        print(f"\n=== 代码库包含 {len(code_files)} 个文件 ===")
        for file_path in code_files.keys():
            print(f"  - {file_path}")
        
        print("\n=== 开始分析... ===")
        result = agent.analyze(SELECTDB_LOGS, code_files)
        print("\n" + result)
    
    # ==================== 方式2: 直接传入日志和代码 ====================
    else:
        # 示例数据 (实际使用时替换为真实数据)
        example_logs = [
            {
                "timestamp": "2026-01-04 10:30:45",
                "level": "ERROR",
                "service": "payment-service",
                "message": "Database connection timeout after 5000ms",
                "exception": "psycopg2.OperationalError: server closed the connection unexpectedly",
                "request_id": "req_12345",
                "context": {
                    "query": "SELECT * FROM orders WHERE status='pending'",
                    "duration_ms": 5000
                }
            },
            {
                "timestamp": "2026-01-04 10:30:46",
                "level": "ERROR",
                "service": "payment-service", 
                "message": "Payment processing failed",
                "exception": "ConnectionError: Unable to connect to database",
                "request_id": "req_12346"
            }
        ]
        
        example_code = {
            "services/payment/service.py": """
import psycopg2
from datetime import datetime

class PaymentService:
    def __init__(self):
        self.db_connection = None
        
    def process_payment(self, order_id: str, amount: float):
        try:
            # 处理支付
            order = self.get_order(order_id)
            # ... 支付处理逻辑
        except Exception as e:
            print(f"Payment processing failed: {e}")
            raise
            
    def get_order(self, order_id: str):
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM orders WHERE id='{order_id}'")
        return cursor.fetchone()
        
    def _get_db_connection(self):
        if not self.db_connection:
            self.db_connection = psycopg2.connect(
                host='localhost',
                port=5432,
                database='payment_db',
                user='admin',
                password='password',
                connect_timeout=5  # 5秒超时
            )
        return self.db_connection
""",
            "config/database.py": """
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'payment_db',
    'user': 'admin',
    'password': 'password',
    'max_connections': 10,
    'connection_timeout': 5
}
"""
        }
        
        print("=== 使用示例数据进行分析... ===")
        print(f"日志数量: {len(example_logs)}")
        print(f"代码文件数: {len(example_code)}")
        
        print("\n=== 开始分析... ===")
        result = agent.analyze(example_logs, example_code)
        print("\n" + result)


if __name__ == "__main__":
    main()
