"""
AI问题排查系统使用示例
"""
import logging
from coordinator_agent import CoordinatorAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 配置DeepSeek API
API_KEY = "sk-94ac4e052ab5486ead278f6bff21db91"
BASE_URL = "https://api.deepseek.com/v1"


def main():
    """主函数：演示问题排查功能"""
    
    print("=" * 80)
    print("AI问题排查系统 - 使用示例")
    print("=" * 80)
    
    # 初始化协调者Agent
    print("\n1. 初始化协调者Agent...")
    coordinator = CoordinatorAgent(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    print("   ✓ 协调者Agent初始化完成")
    
    # 示例1：数据库相关问题排查
    print("\n" + "=" * 80)
    print("示例1：数据库相关问题排查")
    print("=" * 80)
    
    problem1 = "用户表user_table查询速度很慢，响应时间超过5秒，请帮忙排查原因"
    print(f"\n问题描述: {problem1}")
    print("\n开始排查...")
    
    result1 = coordinator.investigate(
        problem_description=problem1,
        max_rounds=3
    )
    
    print(f"\n排查完成!")
    print(f"轮次: {result1['rounds_completed']}")
    print(f"置信度: {result1['confidence']}")
    print(f"\n结论:")
    print(result1['conclusion'])
    
    # 示例2：业务流程问题排查
    print("\n" + "=" * 80)
    print("示例2：业务流程问题排查")
    print("=" * 80)
    
    problem2 = "订单创建流程中，偶尔会出现订单创建失败的情况，错误提示为'数据校验失败'"
    print(f"\n问题描述: {problem2}")
    print("\n开始排查...")
    
    result2 = coordinator.investigate(
        problem_description=problem2,
        max_rounds=3
    )
    
    print(f"\n排查完成!")
    print(f"轮次: {result2['rounds_completed']}")
    print(f"置信度: {result2['confidence']}")
    print(f"\n结论:")
    print(result2['conclusion'])
    
    # 示例3：日志相关问题排查
    print("\n" + "=" * 80)
    print("示例3：日志相关问题排查")
    print("=" * 80)
    
    problem3 = """系统出现空指针异常，错误日志如下：
Exception in thread "main" java.lang.NullPointerException
    at com.example.OrderService.createOrder(OrderService.java:45)
    at com.example.OrderController.create(OrderController.java:23)
请帮忙分析原因"""
    print(f"\n问题描述: {problem3}")
    print("\n开始排查...")
    
    result3 = coordinator.investigate(
        problem_description=problem3,
        max_rounds=3
    )
    
    print(f"\n排查完成!")
    print(f"轮次: {result3['rounds_completed']}")
    print(f"置信度: {result3['confidence']}")
    print(f"\n结论:")
    print(result3['conclusion'])
    
    # 打印汇总信息
    print("\n" + "=" * 80)
    print("排查汇总")
    print("=" * 80)
    print(f"问题1置信度: {result1['confidence']}")
    print(f"问题2置信度: {result2['confidence']}")
    print(f"问题3置信度: {result3['confidence']}")
    
    print("\n" + "=" * 80)
    print("排查完成!")
    print("=" * 80)


def test_individual_agents():
    """测试单个Agent的功能"""
    
    print("\n" + "=" * 80)
    print("测试单个Agent功能")
    print("=" * 80)
    
    from db_agent import DatabaseAgent
    from log_agent import LogAgent
    
    # 测试数据库Agent
    print("\n测试数据库Agent...")
    db_agent = DatabaseAgent(API_KEY, BASE_URL)
    
    result = db_agent.query_object_status(
        object_name="user_table",
        object_type="table"
    )
    print(f"查询结果: {result['status']}")
    
    # 测试日志Agent
    print("\n测试日志Agent...")
    log_agent = LogAgent(API_KEY, BASE_URL)
    
    result = log_agent.query_logs_by_trace_id(
        trace_id="abc123def456"
    )
    print(f"查询结果: {result['status']}")


if __name__ == "__main__":
    # 运行主示例
    main()
    
    # 可选：测试单个Agent
    # test_individual_agents()
