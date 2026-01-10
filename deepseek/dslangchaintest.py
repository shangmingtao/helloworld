from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.agents import create_agent



# 1. LLM
llm = init_chat_model(
    model="deepseek-chat",
    model_provider="openai",
    api_key="sk-94ac4e052ab5486ead278f6bff21db91",
    base_url="https://api.deepseek.com/v1",
    temperature=0,
)

# 2. Tool
@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积"""
    print(f"工具呗调用了{a}{b}")
    return a * b

tools = [multiply]

# 4. Agent
agent = create_agent(
    model=llm,
    tools=tools,
    debug=False,
    system_prompt="You are a helpful assistant"
)



# 6. Run
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "3乘以7等于多少？"}]},
    # stream_mode="updates",
):
    for step, data in chunk.items():
        print(f"step: {step}")
        print(f"content: {data['messages'][-1].content_blocks}")
#Run the agent
# result =agent.invoke(
#     {"messages": [{"role": "user", "content": "3乘以7等于多少？"}]},
#     streaming=False,
#
# )
# print(result)
# print(result.get("output"))
#
# question = {"messages": [{"role": "user", "content": "3乘以7等于多少？"}]}
# print(agent.invoke(question)['messages'][-1].content)


