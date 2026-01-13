import logging
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from prompts import get_code_agent_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
代码查询Agent
功能：接收协调者指令，根据协调者要求查询相关代码片段
方式：代码通过ssh从代码库拉取
"""
class CodeAgent:
    def __init__(self, api_key: str, base_url: str,
                 ssh_host: str = None, ssh_user: str = None, 
                 ssh_password: str = None, code_repo_path: str = None):
        self.api_key = api_key #DeepSeek API密钥
        self.base_url = base_url #DeepSeek 基础URL
        self.ssh_host = ssh_host #SSH主机地址
        self.ssh_user = ssh_user #SSH用户名
        self.ssh_password = ssh_password #SSH密码
        self.code_repo_path = code_repo_path #代码仓库路径
        self.agent = self._create_agent()
        logger.info("CodeAgent.__init__ ===> 代码查询Agent初始化完成")
    
    def _create_agent(self):
        llm = init_chat_model(
            model="deepseek-chat",
            model_provider="openai",
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        
        @tool
        def search_code_by_ssh():
            """
            通过SSH连接代码库，并搜索代码
            """

        tools = [search_code_by_ssh] # 定义工具

        system_prompt = get_code_agent_prompt() # 从prompts文件夹加载系统提示词

        agent = create_agent(  # 创建Agent
            model=llm,
            tools=tools,
            debug=False,
            system_prompt=system_prompt
        )
        
        return agent

    def invoke(self, message: dict) -> dict:
        logger.info(f"CodeAgent.invoke ===> 接收协调者指令: {message}")
        
        try:
            result = self.agent.invoke(message, streaming=False)
            logger.info("查询执行完成")
            return result
            
        except Exception as e:
            logger.error(f"查询执行失败: {str(e)}")
            raise
