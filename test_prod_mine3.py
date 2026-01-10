import time
import uuid
import json
import hmac
import base64
import hashlib
from typing import Optional, Dict, Any

import requests
from urllib.parse import urlencode


def build_headers(headers: dict) -> str:
    """
    将参与签名的 headers 进行 canonical 化
    规则：
    1. 只取 x-ca- 开头的 header（不包含 x-ca-signature）
    2. key 小写
    3. 按 key 字典序排序
    4. 格式：key:value\n
    """
    canonical_headers = []

    for k, v in headers.items():
        k_lower = k.lower()
        if k_lower.startswith("x-ca-") and k_lower != "x-ca-signature":
            canonical_headers.append((k_lower, v))

    canonical_headers.sort(key=lambda x: x[0])

    header_str = ""
    for k, v in canonical_headers:
        header_str += f"{k}:{v}\n"

    return header_str


def build_resource(body: dict) -> str:
    """
    构造参与签名的 resource 字符串
    常见规则：
    - 如果是 POST JSON，一般仍然要求将 body key=value 作为 query 参与签名
    - key 按字典序排序
    """
    if not body:
        return ""

    sorted_items = sorted(body.items(), key=lambda x: x[0])
    return "/queue/basic?" + urlencode(sorted_items)


def test_01():
    try:
        sign_secret = "455742SBSGL53376J52LNEK648MD2W23821I6GQ8"
        url = "https://open.hdltest.com/queue/basic"

        headers = {
            "Authorization": "2e9885dc-6c9f-4a63-ba46-f79798101151",
            "method": "14113",
            "requestId": "1be8e542-e633-442a-9502-af91e05f5414",
            "content-type": "application/json; charset=utf-8",
            "x-ca-timestamp": "1767952373000"
        }

        body = {
            "brandCode": "9898"
        }

        # ================= 构造签名串 =================
        sb = []
        sb.append("POST\n")

        sb.append(headers.get("accept", "") + "\n")
        sb.append(headers.get("content-md5", "") + "\n")
        sb.append(headers.get("content-type", "") + "\n")
        sb.append(headers.get("date", "") + "\n")

        sb.append(build_headers(headers))
        sb.append(build_resource(body))

        sign_string = "".join(sb)

        print("签名串：")
        print(sign_string)

        # ================= 计算 HmacSHA256 =================
        hmac_obj = hmac.new(
            sign_secret.encode("utf-8"),
            sign_string.encode("utf-8"),
            digestmod=hashlib.sha256
        )
        print("base64前签名：", hmac_obj.digest())

        signature = base64.b64encode(hmac_obj.digest()).decode("utf-8")

        print("签名：", signature)

        headers["x-ca-signature"] = signature

        curl_cmd = build_curl_from_requests_post(
            url=url,
            headers=headers,
            json_body=body,
            timeout=15
        )

        print("====== CURL ======")
        print(curl_cmd)

        # ================= 发送请求 =================
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=15
        )
        print("签名:", signature)
        print(f"=======> 请求url:{url}")
        print(f"=======> 返回header:{headers}")
        print(f"=======> 返回body:{body}")
        print("返回结果：")


        print(response.text)

    except Exception as e:
        print("异常：", e)


def build_curl_from_requests_post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: Optional[int] = None
) -> str:
    curl = ["curl"]

    # method
    curl.append("-X POST")

    # headers
    if headers:
        for k, v in headers.items():
            curl.append(f"-H '{k}: {v}'")

    # body
    if json_body is not None:
        body_str = json.dumps(json_body, ensure_ascii=False)
        curl.append(f"-d '{body_str}'")

    # url
    curl.append(f"'{url}'")

    return " ".join(curl)

if __name__ == "__main__":
    test_01()
