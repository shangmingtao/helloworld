"""
测试客户端脚本 - 用于测试API接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """测试注册"""
    print("=== 测试注册 ===")
    data = {
        "username": "testuser",
        "password": "123456",
        "email": "test@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.json().get("token") if response.status_code == 201 else None

def test_login():
    """测试登录"""
    print("\n=== 测试登录 ===")
    data = {
        "username": "testuser",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.json().get("token") if response.status_code == 200 else None

def test_profile(token):
    """测试获取用户信息"""
    print("\n=== 测试获取用户信息 ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

def test_logout(token):
    """测试注销"""
    print("\n=== 测试注销 ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

def main():
    """主测试函数"""
    print("开始测试用户管理API...")
    print(f"服务器地址: {BASE_URL}")
    
    # 先注册一个用户
    token = test_register()
    
    if token:
        print(f"\n获取到令牌: {token}")
        
        # 测试获取用户信息
        test_profile(token)
        
        # 测试注销
        test_logout(token)
    else:
        # 如果注册失败（用户已存在），尝试登录
        print("注册失败，尝试登录...")
        token = test_login()
        
        if token:
            test_profile(token)
            test_logout(token)

if __name__ == "__main__":
    main()