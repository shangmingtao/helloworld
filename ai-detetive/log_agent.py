"""
日志查询Agent
功能：接收coordinator_agent发来的具体要求后完成任务，查询与某日志相关联的日志
关联条件可能是通过traceId返回，通过错误日志调用栈返回
通过将mysql数据库内容向量化后访问
"""
import logging
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from prompts import get_log_agent_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogAgent:
    """日志查询Agent类"""
    
    def __init__(self, api_key: str, base_url: str):
        """
        初始化日志查询Agent
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.agent = self._create_agent()
        logger.info("日志查询Agent初始化完成")
    
    def _create_agent(self):
        """创建日志查询Agent实例"""
        # 初始化LLM
        llm = init_chat_model(
            model="deepseek-chat",
            model_provider="openai",
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        
        # 从prompts文件夹加载系统提示词
        system_prompt = get_log_agent_prompt()
        
        # 创建Agent
        agent = create_agent(
            model=llm,
            tools=[],
            debug=False,
            system_prompt=system_prompt
        )
        
        return agent
    
    def query_logs_by_trace_id(self, trace_id: str) -> dict:
        """
        通过traceId查询关联日志
        
        Args:
            trace_id: 追踪ID
            
        Returns:
            关联日志结果字典
        """
        logger.info(f"开始通过traceId查询日志: {trace_id}")
        
        query = f"请查询traceId为'{trace_id}'的所有关联日志，包括完整的调用链路，"
        query += "请按时间顺序列出日志，并标注关键节点和错误信息"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"traceId日志查询完成: {trace_id}")
            
            return {
                "trace_id": trace_id,
                "status": "success",
                "logs": response
            }
            
        except Exception as e:
            logger.error(f"traceId日志查询失败: {trace_id}, 错误: {str(e)}")
            return {
                "trace_id": trace_id,
                "status": "error",
                "error": str(e)
            }
    
    def query_logs_by_stack_trace(self, stack_trace: str) -> dict:
        """
        通过错误调用栈查询关联日志
        
        Args:
            stack_trace: 错误调用栈
            
        Returns:
            关联日志结果字典
        """
        logger.info("开始通过错误调用栈查询日志")
        
        query = f"请分析以下错误调用栈，并查询相关的日志信息：\n{stack_trace}\n"
        query += "请返回错误发生前后的日志、关联的系统日志和业务日志"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info("错误调用栈日志查询完成")
            
            return {
                "stack_trace": stack_trace,
                "status": "success",
                "logs": response
            }
            
        except Exception as e:
            logger.error(f"错误调用栈日志查询失败: {str(e)}")
            return {
                "stack_trace": stack_trace,
                "status": "error",
                "error": str(e)
            }
    
    def query_logs_by_time_range(self, start_time: str, end_time: str, 
                                  keyword: str = None) -> dict:
        """
        通过时间范围查询日志
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            keyword: 关键词（可选）
            
        Returns:
            日志查询结果字典
        """
        logger.info(f"开始通过时间范围查询日志: {start_time} - {end_time}")
        
        query = f"请查询从{start_time}到{end_time}时间段的日志"
        if keyword:
            query += f"，筛选包含关键词'{keyword}'的日志"
        
        query += "，请按时间顺序列出，并标注重要信息"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info("时间范围日志查询完成")
            
            return {
                "start_time": start_time,
                "end_time": end_time,
                "keyword": keyword,
                "status": "success",
                "logs": response
            }
            
        except Exception as e:
            logger.error(f"时间范围日志查询失败: {str(e)}")
            return {
                "start_time": start_time,
                "end_time": end_time,
                "keyword": keyword,
                "status": "error",
                "error": str(e)
            }
    
    def analyze_log_patterns(self, log_content: str) -> dict:
        """
        分析日志中的模式
        
        Args:
            log_content: 日志内容
            
        Returns:
            模式分析结果字典
        """
        logger.info("开始分析日志模式")
        
        query = f"请分析以下日志内容，识别其中的异常模式、错误规律和潜在问题：\n{log_content}"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info("日志模式分析完成")
            
            return {
                "status": "success",
                "analysis": response
            }
            
        except Exception as e:
            logger.error(f"日志模式分析失败: {str(e)}")
            return {
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
# log_agent = LogAgent(
#     api_key="your-api-key",
#     base_url="https://api.deepseek.com/v1"
# )
