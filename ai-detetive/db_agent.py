"""
数据库查询Agent
功能：接收coordinator_agent发来的具体要求后完成任务，查询数据库对象状态或详细内容
通过将mysql数据库内容向量化后访问
"""
import logging
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from prompts import get_db_agent_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseAgent:
    """数据库查询Agent类"""
    
    def __init__(self, api_key: str, base_url: str):
        """
        初始化数据库Agent
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.agent = self._create_agent()
        logger.info("数据库Agent初始化完成")
    
    def _create_agent(self):
        """创建数据库Agent实例"""
        # 初始化LLM
        llm = init_chat_model(
            model="deepseek-chat",
            model_provider="openai",
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        
        # 从prompts文件夹加载系统提示词
        system_prompt = get_db_agent_prompt()
        
        # 创建Agent
        agent = create_agent(
            model=llm,
            tools=[],
            debug=False,
            system_prompt=system_prompt
        )
        
        return agent
    
    def query_object_status(self, object_name: str, object_type: str = None) -> dict:
        """
        查询数据库对象状态
        
        Args:
            object_name: 对象名称（如表名、索引名等）
            object_type: 对象类型（可选，如table, index等）
            
        Returns:
            查询结果字典
        """
        logger.info(f"开始查询数据库对象状态: {object_name}, 类型: {object_type}")
        
        query = f"请查询数据库对象 {object_name} 的状态信息"
        if object_type:
            query += f"，对象类型为 {object_type}"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"对象状态查询完成: {object_name}")
            
            return {
                "object_name": object_name,
                "object_type": object_type,
                "status": "success",
                "result": response
            }
            
        except Exception as e:
            logger.error(f"查询对象状态失败: {object_name}, 错误: {str(e)}")
            return {
                "object_name": object_name,
                "object_type": object_type,
                "status": "error",
                "error": str(e)
            }
    
    def query_object_details(self, object_name: str, query_type: str = "structure") -> dict:
        """
        查询数据库对象详细内容
        
        Args:
            object_name: 对象名称
            query_type: 查询类型（structure: 结构, data: 数据内容）
            
        Returns:
            查询结果字典
        """
        logger.info(f"开始查询数据库对象详细内容: {object_name}, 查询类型: {query_type}")
        
        query = f"请查询数据库对象 {object_name} 的详细内容"
        if query_type == "structure":
            query += "，重点关注表结构、字段定义、索引信息等"
        elif query_type == "data":
            query += "，重点关注数据内容、数据统计信息等"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"对象详细内容查询完成: {object_name}")
            
            return {
                "object_name": object_name,
                "query_type": query_type,
                "status": "success",
                "result": response
            }
            
        except Exception as e:
            logger.error(f"查询对象详细内容失败: {object_name}, 错误: {str(e)}")
            return {
                "object_name": object_name,
                "query_type": query_type,
                "status": "error",
                "error": str(e)
            }
    
    def analyze_data_issue(self, issue_description: str) -> dict:
        """
        分析数据相关问题
        
        Args:
            issue_description: 问题描述
            
        Returns:
            分析结果字典
        """
        logger.info(f"开始分析数据问题: {issue_description}")
        
        query = f"请分析以下数据问题并提供解决方案：{issue_description}"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info("数据问题分析完成")
            
            return {
                "issue": issue_description,
                "status": "success",
                "result": response
            }
            
        except Exception as e:
            logger.error(f"数据问题分析失败: {str(e)}")
            return {
                "issue": issue_description,
                "status": "error",
                "error": str(e)
            }
    
    def invoke(self, message: dict) -> dict:
        """
        直接调用Agent（供外部使用）
        
        Args:
            message: 消息字典，格式: {"messages": [{"role": "user", "content": "问题内容"}]}
            
        Returns:
            Agent返回结果
        """
        logger.info(f"接收到查询请求: {message}")
        
        try:
            result = self.agent.invoke(message, streaming=False)
            logger.info("查询执行完成")
            return result
            
        except Exception as e:
            logger.error(f"查询执行失败: {str(e)}")
            raise


# 创建全局Agent实例（实际使用时需要配置API密钥）
# db_agent = DatabaseAgent(
#     api_key="your-api-key",
#     base_url="https://api.deepseek.com/v1"
# )
