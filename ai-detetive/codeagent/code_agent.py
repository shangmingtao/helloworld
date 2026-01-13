"""
代码查询Agent
功能：接收coordinator_agent发来的具体要求后完成任务，查询业务对应的代码片段或根据错误日志查询相关代码片段
代码通过ssh从代码库拉取
"""
import logging
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeAgent:
    """代码查询Agent类"""
    
    def __init__(self, api_key: str, base_url: str, 
                 ssh_host: str = None, ssh_user: str = None, 
                 ssh_password: str = None, code_repo_path: str = None):
        """
        初始化代码查询Agent
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
            ssh_host: SSH主机地址
            ssh_user: SSH用户名
            ssh_password: SSH密码
            code_repo_path: 代码仓库路径
        """
        self.api_key = api_key
        self.base_url = base_url
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.code_repo_path = code_repo_path
        self.agent = self._create_agent()
        logger.info("代码查询Agent初始化完成")
    
    def _create_agent(self):
        """创建代码查询Agent实例"""
        # 初始化LLM
        llm = init_chat_model(
            model="deepseek-chat",
            model_provider="openai",
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        
        # 定义工具
        @tool
        def search_code_by_keyword(keyword: str) -> str:
            """
            通过关键词搜索代码
            
            Args:
                keyword: 搜索关键词
                
            Returns:
                搜索结果
            """
            logger.info(f"通过关键词搜索代码: {keyword}")
            # TODO: 实现SSH连接和代码搜索逻辑
            return f"搜索关键词'{keyword}'的代码（需要实现SSH连接和代码搜索）"
        
        @tool
        def get_code_by_path(file_path: str) -> str:
            """
            通过文件路径获取代码
            
            Args:
                file_path: 文件路径
                
            Returns:
                代码内容
            """
            logger.info(f"通过路径获取代码: {file_path}")
            # TODO: 实现SSH连接和代码获取逻辑
            return f"文件'{file_path}'的代码内容（需要实现SSH连接和代码获取）"
        
        @tool
        def search_code_by_function(function_name: str) -> str:
            """
            通过函数名搜索代码
            
            Args:
                function_name: 函数名
                
            Returns:
                搜索结果
            """
            logger.info(f"通过函数名搜索代码: {function_name}")
            # TODO: 实现SSH连接和代码搜索逻辑
            return f"函数'{function_name}'的代码（需要实现SSH连接和代码搜索）"
        
        tools = [search_code_by_keyword, get_code_by_path, search_code_by_function]
        
        # 从prompts文件夹加载系统提示词
        system_prompt = get_code_agent_prompt()
        
        # 创建Agent
        agent = create_agent(
            model=llm,
            tools=tools,
            debug=False,
            system_prompt=system_prompt
        )
        
        return agent
    
    def query_business_code(self, business_name: str) -> dict:
        """
        查询业务对应的代码片段
        
        Args:
            business_name: 业务名称
            
        Returns:
            代码查询结果字典
        """
        logger.info(f"开始查询业务代码: {business_name}")
        
        query = f"请查询业务'{business_name}'对应的代码实现，包括核心逻辑代码、"
        query += "相关函数和类的定义，请提供代码片段和文件位置"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"业务代码查询完成: {business_name}")
            
            return {
                "business_name": business_name,
                "status": "success",
                "code": response
            }
            
        except Exception as e:
            logger.error(f"业务代码查询失败: {business_name}, 错误: {str(e)}")
            return {
                "business_name": business_name,
                "status": "error",
                "error": str(e)
            }
    
    def query_code_by_error_log(self, error_log: str, stack_trace: str = None) -> dict:
        """
        根据错误日志查询相关代码片段
        
        Args:
            error_log: 错误日志
            stack_trace: 调用栈（可选）
            
        Returns:
            代码查询结果字典
        """
        logger.info("开始根据错误日志查询代码")
        
        query = f"请根据以下错误日志查询相关代码：\n{error_log}\n"
        if stack_trace:
            query += f"\n调用栈信息：\n{stack_trace}\n"
        query += "请定位错误发生的代码位置，并分析问题原因"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info("错误日志代码查询完成")
            
            return {
                "error_log": error_log,
                "stack_trace": stack_trace,
                "status": "success",
                "code": response
            }
            
        except Exception as e:
            logger.error(f"错误日志代码查询失败: {str(e)}")
            return {
                "error_log": error_log,
                "stack_trace": stack_trace,
                "status": "error",
                "error": str(e)
            }
    
    def analyze_code_logic(self, function_name: str, business_context: str = None) -> dict:
        """
        分析代码逻辑
        
        Args:
            function_name: 函数名
            business_context: 业务上下文（可选）
            
        Returns:
            代码逻辑分析结果字典
        """
        logger.info(f"开始分析代码逻辑: {function_name}")
        
        query = f"请分析函数'{function_name}'的代码逻辑，包括输入输出、处理流程、"
        query += "边界条件和异常处理"
        
        if business_context:
            query += f"，在{business_context}业务上下文中分析"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"代码逻辑分析完成: {function_name}")
            
            return {
                "function_name": function_name,
                "business_context": business_context,
                "status": "success",
                "analysis": response
            }
            
        except Exception as e:
            logger.error(f"代码逻辑分析失败: {function_name}, 错误: {str(e)}")
            return {
                "function_name": function_name,
                "business_context": business_context,
                "status": "error",
                "error": str(e)
            }
    
    def search_code_by_pattern(self, pattern: str, file_pattern: str = None) -> dict:
        """
        按模式搜索代码
        
        Args:
            pattern: 代码模式
            file_pattern: 文件模式（可选）
            
        Returns:
            代码搜索结果字典
        """
        logger.info(f"开始按模式搜索代码: {pattern}")
        
        query = f"请搜索符合模式'{pattern}'的代码"
        if file_pattern:
            query += f"，在文件模式'{file_pattern}'中搜索"
        query += "，请提供匹配的代码片段和文件位置"
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info(f"代码模式搜索完成: {pattern}")
            
            return {
                "pattern": pattern,
                "file_pattern": file_pattern,
                "status": "success",
                "results": response
            }
            
        except Exception as e:
            logger.error(f"代码模式搜索失败: {pattern}, 错误: {str(e)}")
            return {
                "pattern": pattern,
                "file_pattern": file_pattern,
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
# code_agent = CodeAgent(
#     api_key="your-api-key",
#     base_url="https://api.deepseek.com/v1",
#     ssh_host="your-ssh-host",
#     ssh_user="your-ssh-user",
#     ssh_password="your-ssh-password",
#     code_repo_path="/path/to/repo"
# )
