"""
协调者Agent (Coordinator Agent)
功能：负责问题排查流程自主编排、问题排查结果回归验证、置信度评估、循环次数控制
包含5个tools：db_collector、dld_collector、log_collector、prd_collector、code_collector
每个tool内部调用对应的agent
"""
import logging
from typing import Dict, List, Optional
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from prompts import get_coordinator_agent_prompt

# 导入各个子Agent
from db_agent import DatabaseAgent
from dld_agent import BusinessLogicAgent
from log_agent import LogAgent
from prd_agent import PRDAgent
from code_agent import CodeAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """协调者Agent类，负责问题排查流程编排"""
    
    def __init__(self, api_key: str, base_url: str):
        """
        初始化协调者Agent
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        
        # 初始化各个子Agent
        self.db_agent = DatabaseAgent(api_key, base_url)
        self.dld_agent = BusinessLogicAgent(api_key, base_url)
        self.log_agent = LogAgent(api_key, base_url)
        self.prd_agent = PRDAgent(api_key, base_url)
        self.code_agent = CodeAgent(api_key, base_url)
        
        # 创建协调者Agent
        self.agent = self._create_agent()
        
        # 问题排查状态
        self.investigation_state = {
            "current_round": 0,
            "max_rounds": 3,
            "confidence": 0.0,
            "findings": [],
            "actions_taken": []
        }
        
        logger.info("协调者Agent初始化完成")
    
    def _create_agent(self):
        """创建协调者Agent实例"""
        # 初始化LLM
        llm = init_chat_model(
            model="deepseek-chat",
            model_provider="openai",
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        
        # 定义工具（封装子Agent调用）
        @tool
        def db_collector(query: str) -> str:
            """
            数据库查询工具：查询数据库对象状态、详细内容或分析数据问题
            
            Args:
                query: 查询要求，描述需要查询的数据库对象或问题
                
            Returns:
                查询结果
            """
            logger.info(f"调用db_collector: {query}")
            try:
                result = self.db_agent.invoke(
                    {"messages": [{"role": "user", "content": query}]}
                )
                content = result.get("messages")[-1].content
                
                # 记录已执行的操作
                self.investigation_state["actions_taken"].append({
                    "tool": "db_collector",
                    "query": query,
                    "result": content
                })
                
                logger.info(f"db_collector执行完成")
                return content
            except Exception as e:
                logger.error(f"db_collector执行失败: {str(e)}")
                return f"数据库查询失败: {str(e)}"
        
        @tool
        def dld_collector(query: str) -> str:
            """
            业务流程查询工具：查询业务流程的实现路径、关键步骤或分析流程问题
            
            Args:
                query: 查询要求，描述需要查询的业务流程或问题
                
            Returns:
                查询结果
            """
            logger.info(f"调用dld_collector: {query}")
            try:
                result = self.dld_agent.invoke(
                    {"messages": [{"role": "user", "content": query}]}
                )
                content = result.get("messages")[-1].content
                
                # 记录已执行的操作
                self.investigation_state["actions_taken"].append({
                    "tool": "dld_collector",
                    "query": query,
                    "result": content
                })
                
                logger.info(f"dld_collector执行完成")
                return content
            except Exception as e:
                logger.error(f"dld_collector执行失败: {str(e)}")
                return f"业务流程查询失败: {str(e)}"
        
        @tool
        def log_collector(query: str) -> str:
            """
            日志查询工具：查询关联日志，支持通过traceId、错误调用栈等方式查询
            
            Args:
                query: 查询要求，描述需要查询的日志或查询条件
                
            Returns:
                查询结果
            """
            logger.info(f"调用log_collector: {query}")
            try:
                result = self.log_agent.invoke(
                    {"messages": [{"role": "user", "content": query}]}
                )
                content = result.get("messages")[-1].content
                
                # 记录已执行的操作
                self.investigation_state["actions_taken"].append({
                    "tool": "log_collector",
                    "query": query,
                    "result": content
                })
                
                logger.info(f"log_collector执行完成")
                return content
            except Exception as e:
                logger.error(f"log_collector执行失败: {str(e)}")
                return f"日志查询失败: {str(e)}"
        
        @tool
        def prd_collector(query: str) -> str:
            """
            产品需求查询工具：查询业务逻辑、业务规则或业务场景
            
            Args:
                query: 查询要求，描述需要查询的业务逻辑或需求
                
            Returns:
                查询结果
            """
            logger.info(f"调用prd_collector: {query}")
            try:
                result = self.prd_agent.invoke(
                    {"messages": [{"role": "user", "content": query}]}
                )
                content = result.get("messages")[-1].content
                
                # 记录已执行的操作
                self.investigation_state["actions_taken"].append({
                    "tool": "prd_collector",
                    "query": query,
                    "result": content
                })
                
                logger.info(f"prd_collector执行完成")
                return content
            except Exception as e:
                logger.error(f"prd_collector执行失败: {str(e)}")
                return f"产品需求查询失败: {str(e)}"
        
        @tool
        def code_collector(query: str) -> str:
            """
            代码查询工具：查询业务对应的代码片段或根据错误日志查询相关代码
            
            Args:
                query: 查询要求，描述需要查询的代码或错误信息
                
            Returns:
                查询结果
            """
            logger.info(f"调用code_collector: {query}")
            try:
                result = self.code_agent.invoke(
                    {"messages": [{"role": "user", "content": query}]}
                )
                content = result.get("messages")[-1].content
                
                # 记录已执行的操作
                self.investigation_state["actions_taken"].append({
                    "tool": "code_collector",
                    "query": query,
                    "result": content
                })
                
                logger.info(f"code_collector执行完成")
                return content
            except Exception as e:
                logger.error(f"code_collector执行失败: {str(e)}")
                return f"代码查询失败: {str(e)}"
        
        tools = [db_collector, dld_collector, log_collector, prd_collector, code_collector]
        
        # 从prompts文件夹加载系统提示词
        system_prompt = get_coordinator_agent_prompt()
        
        # 创建Agent
        agent = create_agent(
            model=llm,
            tools=tools,
            debug=False,
            system_prompt=system_prompt
        )
        
        return agent
    
    def investigate(self, problem_description: str, 
                   max_rounds: int = 3) -> Dict:
        """
        执行问题排查
        
        Args:
            problem_description: 问题描述
            max_rounds: 最大排查轮数
            
        Returns:
            排查结果字典
        """
        logger.info(f"开始问题排查: {problem_description}")
        logger.info(f"最大排查轮数: {max_rounds}")
        
        # 重置排查状态
        self.investigation_state = {
            "current_round": 0,
            "max_rounds": max_rounds,
            "confidence": 0.0,
            "findings": [],
            "actions_taken": []
        }
        
        # 构建初始查询
        query = f"""请协助排查以下技术问题：
问题描述：{problem_description}

请按照以下步骤进行排查：
1. 理解问题，识别关键信息
2. 设计排查方案，选择合适的工具
3. 收集相关信息
4. 分析问题根因
5. 验证分析结果
6. 给出结论和建议

请在每一步说明你的思考过程和使用的工具。"""
        
        try:
            # 执行排查
            for round_num in range(1, max_rounds + 1):
                logger.info(f"=== 开始第 {round_num} 轮排查 ===")
                self.investigation_state["current_round"] = round_num
                
                # 调用协调者Agent
                if round_num == 1:
                    # 第一轮使用初始查询
                    result = self.agent.invoke(
                        {"messages": [{"role": "user", "content": query}]},
                        streaming=False
                    )
                else:
                    # 后续轮次根据上一轮结果继续深入
                    last_result = self.investigation_state["findings"][-1]
                    follow_up_query = f"""上一轮排查结果如下：
{last_result}

请根据以上结果，判断是否需要进一步排查。如果需要，请继续深入调查；如果已经找到明确的根因和解决方案，请总结最终结果并给出置信度评分。"""
                    
                    result = self.agent.invoke(
                        {"messages": [{"role": "user", "content": follow_up_query}]},
                        streaming=False
                    )
                
                # 获取结果
                response = result.get("messages")[-1].content
                self.investigation_state["findings"].append({
                    "round": round_num,
                    "result": response
                })
                
                logger.info(f"第 {round_num} 轮排查完成")
                logger.info(f"本轮结果: {response[:200]}...")
                
                # 检查是否已经找到明确答案
                if "结论" in response or "根因" in response or "置信度" in response:
                    logger.info("已找到明确答案，结束排查")
                    break
            
            # 汇总最终结果
            final_result = self._summarize_investigation()
            logger.info(f"问题排查完成，置信度: {final_result['confidence']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"问题排查失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "investigation_state": self.investigation_state
            }
    
    def _summarize_investigation(self) -> Dict:
        """
        汇总排查结果
        
        Returns:
            汇总结果字典
        """
        logger.info("开始汇总排查结果")
        
        # 获取最后一轮结果作为主要结论
        if self.investigation_state["findings"]:
            last_finding = self.investigation_state["findings"][-1]["result"]
        else:
            last_finding = "未获得有效结果"
        
        # 尝试从结果中提取置信度
        confidence = self._extract_confidence(last_finding)
        
        summary = {
            "status": "success",
            "problem": "技术问题排查",
            "rounds_completed": self.investigation_state["current_round"],
            "confidence": confidence,
            "findings": self.investigation_state["findings"],
            "actions_taken": self.investigation_state["actions_taken"],
            "conclusion": last_finding
        }
        
        logger.info("排查结果汇总完成")
        return summary
    
    def _extract_confidence(self, text: str) -> float:
        """
        从文本中提取置信度评分
        
        Args:
            text: 包含置信度信息的文本
            
        Returns:
            置信度评分（0-100）
        """
        import re
        
        # 尝试匹配"置信度"关键词
        patterns = [
            r"置信度[：:]\s*(\d+)",
            r"置信度[为是]\s*(\d+)",
            r"confidence[：:]\s*(\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    confidence = float(match.group(1))
                    # 确保在0-100范围内
                    return max(0.0, min(100.0, confidence))
                except (ValueError, IndexError):
                    continue
        
        # 未找到明确置信度，返回默认值
        return 50.0
    
    def verify_result(self, verification_query: str) -> Dict:
        """
        验证排查结果
        
        Args:
            verification_query: 验证查询
            
        Returns:
            验证结果字典
        """
        logger.info(f"开始验证排查结果: {verification_query}")
        
        query = f"""请验证以下排查结果的准确性：
验证内容：{verification_query}

已有的排查结果：
{self.investigation_state.get('findings', [])}

请使用相关工具进行验证，并说明验证结果是否支持原结论。"""
        
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                streaming=False
            )
            
            response = result.get("messages")[-1].content
            logger.info("排查结果验证完成")
            
            return {
                "status": "success",
                "verification_query": verification_query,
                "result": response
            }
            
        except Exception as e:
            logger.error(f"排查结果验证失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def invoke(self, message: dict) -> dict:
        """
        直接调用Agent（供外部使用）
        
        Args:
            message: 消息字典
            
        Returns:
            Agent返回结果
        """
        logger.info(f"接收到请求: {message}")
        
        try:
            result = self.agent.invoke(message, streaming=False)
            logger.info("请求执行完成")
            return result
            
        except Exception as e:
            logger.error(f"请求执行失败: {str(e)}")
            raise


# 创建全局Agent实例（实际使用时需要配置API密钥）
# coordinator = CoordinatorAgent(
#     api_key="your-api-key",
#     base_url="https://api.deepseek.com/v1"
# )
