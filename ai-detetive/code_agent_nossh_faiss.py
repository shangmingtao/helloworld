import logging
import faiss
import numpy as np
import pickle

from langchain_core.tools import Tool
from openai import OpenAI
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
方式：通过FAISS向量数据库检索代码
"""
class CodeAgent:
    def __init__(self, api_key: str, base_url: str,
                 embedding_api_key: str = None, embedding_base_url: str = None,
                 faiss_index_path: str = "faiss_index.bin",
                 faiss_metadata_path: str = "faiss_metadata.pkl"):
        self.api_key = api_key # DeepSeek API密钥
        self.base_url = base_url # DeepSeek 基础URL
        self.embedding_api_key = embedding_api_key # 向量化API密钥
        self.embedding_base_url = embedding_base_url # 向量化基础URL
        self.faiss_index_path = faiss_index_path # FAISS索引文件路径
        self.faiss_metadata_path = faiss_metadata_path # FAISS元数据文件路径
        
        # 初始化向量模型客户端
        if self.embedding_api_key and self.embedding_base_url:
            self.embedding_client = OpenAI(api_key=self.embedding_api_key, base_url=self.embedding_base_url)
        else:
            self.embedding_client = None
        
        # 加载FAISS索引和元数据
        self._load_faiss_index()
        
        # 创建Agent
        self.agent = self._create_agent()
        logger.info("CodeAgent.__init__ ===> 代码查询Agent初始化完成")
    
    def _load_faiss_index(self):
        """加载FAISS索引和元数据"""
        try:
            # 加载FAISS索引
            self.faiss_index = faiss.read_index(self.faiss_index_path)
            logger.info(f"成功加载FAISS索引: {self.faiss_index_path}, 向量维度: {self.faiss_index.d}")
            
            # 加载元数据
            with open(self.faiss_metadata_path, 'rb') as f:
                self.metadata_list = pickle.load(f)
            logger.info(f"成功加载元数据: {self.faiss_metadata_path}, 共 {len(self.metadata_list)} 条记录")
            
        except Exception as e:
            logger.error(f"加载FAISS索引失败: {str(e)}")
            raise
    
    def _create_agent(self):
        """创建DeepSeek大模型Agent"""
        llm = init_chat_model(
            model="deepseek-chat",
            model_provider="openai",
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        
        @tool
        def search_code_by_faiss(query: str) -> str:
            """根据用户查询的中文表述检索相关代码块"""

            return self._search_code(query)

        # tools = [
        #     Tool(
        #         name="search_code_by_faiss",
        #         func=search_code_by_faiss,
        #         description="根据用户的中文描述查询代码片段"
        #     )
        # ]
        tools = [search_code_by_faiss] # 定义工具

        system_prompt = """
你是一个代码查找专家，专门给用户查询用户想要的代码。

你的职责：
1. 根据用户要求查询对应的代码，详细按照调用链路罗列完整的相关核心代码
2. 用户输入一个要求后你可以选择对应tools查询

工作方法：
- 根据获取到的代码调用栈逐层递进，直至穷尽
- 如果涉及数据库操作，要根据Mapper找到对应的xml，并将相关部分sql呈现出来
- 你要以一个专业研发人员的身份来进行代码阅读，而不是分散阅读
- 不允许你进行方法内部的代码省略、简述、自行总结，要完整呈现逻辑

输出格式要求：
- 提供完整的相关代码，包含上下文，不要只提供代码片段，不要省略代码
- 说明代码的位置和文件路径

注意事项：
- 不需要你分析代码
- 不允许你进行方法内部的代码省略、简述、自行总结，要完整呈现逻辑
- 使用工具来搜索和获取代码，不要凭空编造代码内容
        """

        agent = create_agent(  # 创建Agent
            model=llm,
            tools=tools,
            debug=False,
            system_prompt=system_prompt
        )
        
        return agent
    
    def _search_code(self, query: str) -> str:
        """
        根据用户查询的中文表述检索相关代码块

        Args:
            query: 用户想要查询的代码模块的中文表述

        Returns:
            对应的代码块
        """
        if not self.embedding_client:
            raise ValueError("未配置向量化API客户端，无法执行查询")
        
        try:
            # 生成查询向量
            logger.info(f"正在生成查询向量: {query}")
            response = self.embedding_client.embeddings.create(
                model="text-embedding-v4",
                input=query
            )
            query_vector = np.array([response.data[0].embedding], dtype='float32')
            
            # 在FAISS索引中搜索
            k = 8  # 返回最相关的3个结果
            distances, indices = self.faiss_index.search(query_vector, k)
            
            # 获取匹配的文档
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata_list):
                    doc = self.metadata_list[idx]
                    results.append({
                        'distance': float(distances[0][i]),
                        'content': doc.page_content,
                        'metadata': doc.metadata
                    })
            
            # 格式化返回结果
            if not results:
                return "未找到相关代码"
            
            response_text = f"找到 {len(results)} 个相关代码片段:\n\n"
            for i, result in enumerate(results, 1):
                response_text += f"=== 结果 {i} (相似度: {1 - result['distance']:.4f}) ===\n"
                response_text += f"文件: {result['metadata'].get('file_path', '未知')}\n"
                response_text += f"代码:\n{result['content']}\n\n"
            
            logger.info(f"查询完成，返回 {len(results)} 个结果")
            return response_text
            
        except Exception as e:
            logger.error(f"检索代码失败: {str(e)}")
            raise
    
    def search_code(self, query: str) -> str:
        """
        公开方法：根据用户查询的中文表述检索相关代码块

        Args:
            query: 用户想要查询的代码模块的中文表述

        Returns:
            对应的代码块
        """
        return self._search_code(query)

    def invoke(self, message: dict) -> dict:
        print(f"CodeAgent.invoke ===> 接收协调者指令: {message}")
        
        try:
            result = self.agent.invoke(message, streaming=False)
            logger.info("查询执行完成")
            return result
            
        except Exception as e:
            logger.error(f"查询执行失败: {str(e)}")
            raise


if __name__ == "__main__":
    # 配置API密钥
    DEEPSEEK_API_KEY = "sk-94ac4e052ab5486ead278f6bff21db91"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    EMBEDDING_API_KEY = "sk-b5f310af8681408dafc4ee99f278c18e"
    EMBEDDING_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 配置FAISS文件路径
    FAISS_INDEX_PATH = "faiss_index.bin"
    FAISS_METADATA_PATH = "faiss_metadata.pkl"
    
    # 初始化CodeAgent
    print("正在初始化CodeAgent...")
    code_agent = CodeAgent(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        embedding_api_key=EMBEDDING_API_KEY,
        embedding_base_url=EMBEDDING_BASE_URL,
        faiss_index_path=FAISS_INDEX_PATH,
        faiss_metadata_path=FAISS_METADATA_PATH
    )
    
    # # 测试查询
    # print("\n" + "="*60)
    # print("测试查询功能")
    # print("="*60)
    #
    # # 方法1：直接调用search_code方法
    # test_query = "注册 密码加密"
    # print(f"\n查询: {test_query}")
    # print("-"*60)
    # result = code_agent.search_code(test_query)
    # print(result)
    
    # 方法2：通过Agent调用
    # response = code_agent.invoke({"messages": [{"role": "user", "content": "查询 kpad盘点任务历史 业务的相关代码"}]})
    response = code_agent.invoke({"messages": [{"role": "user", "content": "查询takingHistory方法代码,包括方法内部调用的其他方法，要完整呈现这部分代码"}]})
    # response = code_agent.invoke({"messages": [{"role": "user", "content": "退出登录"}]})
    print(f"大模型返回 ====> {response}")
    print(response['messages'][-1].content)
    # # 6. Run
    # for chunk in code_agent.stream(
    #         {"messages": [{"role": "user", "content": "用户登录功能"}]},
    #         # stream_mode="updates",
    # ):
    #     for step, data in chunk.items():
    #         print(f"step: {step}")
    #         print(f"content: {data['messages'][-1].content_blocks}")
