"""
产品需求Agent
功能：接收coordinator_agent发来的具体要求后完成任务，查询某业务流程的业务逻辑
"""
import logging
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from prompts import get_prd_agent_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PRDAgent:
    """产品需求Agent类"""
    
    def __init__(self, api_key: str, base_url: str):
        """
        初始化产品需求Agent
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.agent = self._create_agent()
        logger.info("产品需求Agent初始化完成")
    
    def _create_agent(self):
        """创建产品需求Agent实例"""
        # 初始化LLM
        llm = init_chat_model(
            model="deepseek-chat",
            model_provider="openai",
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        
        # 从prompts文件夹加载系统提示词
        system_prompt = get_prd_agent_prompt()
        
        # 创建Agent
        agent = create_agent(
            model=llm,
            tools=[],
            debug=False,
            system_prompt=system_prompt
        )
        
        return agent
    
    def query_business_logic(self, business_name: str) -> dict:
        """
        查询业务逻辑
        
        Args:
            business_name: 业务名称
            
        Returns:
            业务逻辑描述字典
        """
        logger.info(f"开始查询业务逻辑: {business_name}")
        
        query = f"请详细说明业务'{business_name}'的业务逻辑，包括核心流程、业务规则、"
        query += "约束条件、边界条件和特殊情况"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"业务逻辑查询完成: {business_name}")
            
            return {
                "business_name": business_name,
                "status": "success",
                "logic": response
            }
            
        except Exception as e:
            logger.error(f"业务逻辑查询失败: {business_name}, 错误: {str(e)}")
            return {
                "business_name": business_name,
                "status": "error",
                "error": str(e)
            }
    
    def explain_business_rule(self, rule_name: str, context: str = None) -> dict:
        """
        解释业务规则
        
        Args:
            rule_name: 规则名称
            context: 业务上下文（可选）
            
        Returns:
            规则解释字典
        """
        logger.info(f"开始解释业务规则: {rule_name}")
        
        query = f"请详细解释业务规则'{rule_name}'，包括规则的定义、应用场景、"
        query += "约束条件和影响范围"
        
        if context:
            query += f"，在{context}上下文中解释"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"业务规则解释完成: {rule_name}")
            
            return {
                "rule_name": rule_name,
                "context": context,
                "status": "success",
                "explanation": response
            }
            
        except Exception as e:
            logger.error(f"业务规则解释失败: {rule_name}, 错误: {str(e)}")
            return {
                "rule_name": rule_name,
                "context": context,
                "status": "error",
                "error": str(e)
            }
    
    def analyze_business_scenario(self, scenario_description: str) -> dict:
        """
        分析业务场景
        
        Args:
            scenario_description: 场景描述
            
        Returns:
            场景分析结果字典
        """
        logger.info(f"开始分析业务场景: {scenario_description}")
        
        query = f"请分析以下业务场景，说明预期的业务行为、处理逻辑和可能的结果：{scenario_description}"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info("业务场景分析完成")
            
            return {
                "scenario": scenario_description,
                "status": "success",
                "analysis": response
            }
            
        except Exception as e:
            logger.error(f"业务场景分析失败: {str(e)}")
            return {
                "scenario": scenario_description,
                "status": "error",
                "error": str(e)
            }
    
    def compare_requirement_implementation(self, requirement: str, 
                                          implementation: str = None) -> dict:
        """
        对比需求和实现
        
        Args:
            requirement: 需求描述
            implementation: 实现描述（可选）
            
        Returns:
            对比结果字典
        """
        logger.info("开始对比需求和实现")
        
        query = f"请分析以下业务需求，并说明预期的实现方式：{requirement}"
        if implementation:
            query += f"\n当前实现方式：{implementation}\n请对比需求与实现的差异"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info("需求和实现对比完成")
            
            return {
                "requirement": requirement,
                "implementation": implementation,
                "status": "success",
                "comparison": response
            }
            
        except Exception as e:
            logger.error(f"需求和实现对比失败: {str(e)}")
            return {
                "requirement": requirement,
                "implementation": implementation,
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
# prd_agent = PRDAgent(
#     api_key="your-api-key",
#     base_url="https://api.deepseek.com/v1"
# )
