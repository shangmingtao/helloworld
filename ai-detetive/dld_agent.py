"""
业务流程Agent
功能：接收coordinator_agent发来的具体要求后完成任务，查询业务流程的实现路径
返回示例：先查询数据库-进行数据比对-删除数据-给用户返回成功，删除数据失败-给用户返回失败
"""
import logging
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from prompts import get_dld_agent_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessLogicAgent:
    """业务流程Agent类"""
    
    def __init__(self, api_key: str, base_url: str):
        """
        初始化业务流程Agent
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.agent = self._create_agent()
        logger.info("业务流程Agent初始化完成")
    
    def _create_agent(self):
        """创建业务流程Agent实例"""
        # 初始化LLM
        llm = init_chat_model(
            model="deepseek-chat",
            model_provider="openai",
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        
        # 从prompts文件夹加载系统提示词
        system_prompt = get_dld_agent_prompt()
        
        # 创建Agent
        agent = create_agent(
            model=llm,
            tools=[],
            debug=False,
            system_prompt=system_prompt
        )
        
        return agent
    
    def get_business_flow(self, business_name: str, scenario: str = None) -> dict:
        """
        获取业务流程的实现路径
        
        Args:
            business_name: 业务名称
            scenario: 业务场景（可选，如正常流程、异常流程等）
            
        Returns:
            业务流程描述字典
        """
        logger.info(f"开始获取业务流程: {business_name}, 场景: {scenario}")
        
        query = f"请详细分析业务流程'{business_name}'在研发实现中的完整路径，"
        query += "包括所有步骤、数据流转、异常处理逻辑等"
        
        if scenario:
            query += f"，重点关注{scenario}场景"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"业务流程查询完成: {business_name}")
            
            return {
                "business_name": business_name,
                "scenario": scenario,
                "status": "success",
                "flow": response
            }
            
        except Exception as e:
            logger.error(f"获取业务流程失败: {business_name}, 错误: {str(e)}")
            return {
                "business_name": business_name,
                "scenario": scenario,
                "status": "error",
                "error": str(e)
            }
    
    def analyze_flow_issue(self, business_name: str, issue_description: str) -> dict:
        """
        分析业务流程中的问题
        
        Args:
            business_name: 业务名称
            issue_description: 问题描述
            
        Returns:
            问题分析结果字典
        """
        logger.info(f"开始分析业务流程问题: {business_name}, 问题: {issue_description}")
        
        query = f"请分析业务流程'{business_name}'中出现的以下问题：{issue_description}"
        query += "请说明问题发生的位置、原因和可能的解决方案"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"业务流程问题分析完成: {business_name}")
            
            return {
                "business_name": business_name,
                "issue": issue_description,
                "status": "success",
                "analysis": response
            }
            
        except Exception as e:
            logger.error(f"业务流程问题分析失败: {business_name}, 错误: {str(e)}")
            return {
                "business_name": business_name,
                "issue": issue_description,
                "status": "error",
                "error": str(e)
            }
    
    def get_flow_steps(self, business_name: str) -> dict:
        """
        获取业务流程的关键步骤列表
        
        Args:
            business_name: 业务名称
            
        Returns:
            步骤列表字典
        """
        logger.info(f"开始获取业务流程步骤: {business_name}")
        
        query = f"请列出业务流程'{business_name}'的所有关键步骤，包括步骤名称、输入、输出和依赖关系"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"业务流程步骤获取完成: {business_name}")
            
            return {
                "business_name": business_name,
                "status": "success",
                "steps": response
            }
            
        except Exception as e:
            logger.error(f"获取业务流程步骤失败: {business_name}, 错误: {str(e)}")
            return {
                "business_name": business_name,
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
# dld_agent = BusinessLogicAgent(
#     api_key="your-api-key",
#     base_url="https://api.deepseek.com/v1"
# )
