import json
import time
import uuid
import base64
import hmac
import hashlib
import requests
from collections import OrderedDict


def build_headers(headers: dict) -> str:
    """
    将 x-ca-* headers 按字母序拼接成签名字符串
    同时写入 x-ca-signature-headers
    """
    headers_to_sign = OrderedDict()
    sign_header_keys = []

    for k in sorted(headers.keys()):
        if k.startswith("x-ca-"):
            if k in ("x-ca-signature", "x-ca-signature-headers"):
                continue
            sign_header_keys.append(k)
            headers_to_sign[k] = headers[k]

    headers["x-ca-signature-headers"] = ",".join(sign_header_keys)

    sb = []
    for k, v in headers_to_sign.items():
        sb.append(f"{k}:{v}\n")

    header_str = "".join(sb)
    print("header是:\n", header_str)
    return header_str


def build_resource(body: dict) -> str:
    """
    拼接 path + query 参数
    """
    result = "/queue/basic"

    if body:
        params = OrderedDict(sorted(body.items()))
        query = []
        for k, v in params.items():
            if v is not None and v != "":
                query.append(f"{k}={v}")
            else:
                query.append(k)
        result += "?" + "&".join(query)

    return result


def build_string_to_sign(headers: dict, body: dict) -> str:
    """
    构造最终签名串
    """
    sb = []

    sb.append("POST\n")

    sb.append(headers.get("accept", "*/*")) #python框架底层在accept不传时，默认帮忙补传*/*，与java okhttp实现不同
    sb.append("\n")

    sb.append(headers.get("content-md5", ""))
    sb.append("\n")

    sb.append(headers.get("content-type", ""))
    sb.append("\n")

    sb.append(headers.get("date", ""))
    sb.append("\n")

    sb.append(build_headers(headers))
    sb.append(build_resource(body))

    sign_str = "".join(sb)
    # sign_str = sign_str.replace("*/*", "")
    print(sign_str)
    return sign_str


def hmac_sha256_base64(secret: str, msg: str) -> str:
    """
    HmacSHA256 + Base64
    """
    digest = hmac.new(
        secret.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def test_01():
    # ========= 账号信息 =========
    client_id = "client_id"
    client_secret = "client_secret"
    sign_secret = "sign_secret"

    url = "https://open.hdltest.com/queue/basic"
    token_url = (
        "https://open.hdltest.com/oauth/token"
        "?grant_type=client_credentials"
        "&scope=sever"
        f"&client_id={client_id}"
        f"&client_secret={client_secret}"
    )

    session = requests.Session()
    session.timeout = 15

    # ========= 获取 token =========
    token_resp = session.post(token_url)
    token_resp.raise_for_status()
    token = token_resp.json().get("access_token")
    print("token是:", token)

    # ========= 构造 header =========
    headers = {
        "Authorization": token,
        "method": "14113",
        "requestId": str(uuid.uuid4()),
        "content-type": "application/json; charset=utf-8",
        "x-ca-timestamp": str(int(time.time() * 1000)),
        "accept":"*/*"
    }

    # ========= 请求 body =========
    body = {
        "brandCode": "9898"
    }

    # ========= 生成签名 =========
    string_to_sign = build_string_to_sign(headers, body)
    signature = hmac_sha256_base64(sign_secret, string_to_sign)
    print("签名:", signature)

    headers["x-ca-signature"] = signature

    # ========= 发送请求 =========
    resp = session.post(
        url,
        headers=headers,
        json=body
    )
    resp.raise_for_status()
    print("响应结果:", resp.text)

    print("签名:", signature)
    print(f"=======> 请求url:{url}")
    print(f"=======> 返回header:{headers}")
    print(f"=======> 返回body:{body}")
    print("返回结果：")


if __name__ == "__main__":
    test_01()
