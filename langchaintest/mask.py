import os
import sys

def mask_key(k: str) -> str:
    if not k:
        return "<EMPTY>"
    # 只显示前6 + 后4，避免泄露
    return f"{k[:6]}...{k[-4:]} (len={len(k)})"

print("Python executable:", sys.executable)

api_key = os.getenv("OPENAI_API_KEY", "")
print("OPENAI_API_KEY:", mask_key(api_key))

try:
    import openai
    print("openai version:", getattr(openai, "__version__", "<unknown>"))
except Exception as e:
    print("openai import failed:", repr(e))

if not api_key:
    raise RuntimeError("未读取到 OPENAI_API_KEY。请重启 Spyder/终端后再试。")

# API 调用
# try:
#     from openai import OpenAI
#     client = OpenAI()  # 默认从环境变量 OPENAI_API_KEY 读取 :contentReference[oaicite:0]{index=0}

#     resp = client.responses.create(
#         model="gpt-5.2",
#         input="Hello! Reply with one short sentence."
#     )
#     print("API OK. output_text:", resp.output_text)

# except Exception as e:
#     print("API call failed:", repr(e))
