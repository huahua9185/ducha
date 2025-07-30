#!/usr/bin/env python3
"""
快速HTTP测试
"""

import requests
import json

def test_api():
    print("开始API测试...")
    
    try:
        # 测试健康检查
        print("1. 测试健康检查...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("[PASS] 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"[FAIL] 健康检查失败: {response.status_code}")
            return
        
        # 测试ping
        print("\\n2. 测试ping...")
        response = requests.get("http://localhost:8000/api/v1/ping", timeout=10)
        if response.status_code == 200:
            print("[PASS] Ping测试通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"[FAIL] Ping测试失败: {response.status_code}")
        
        # 测试登录
        print("\\n3. 测试登录...")
        login_data = {
            "username": "test_admin",
            "password": "test123456"
        }
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("[PASS] 登录测试通过")
            token = result["data"]["access_token"]
            print(f"   获取到token: {token[:20]}...")
            
            # 使用token测试其他API
            headers = {"Authorization": f"Bearer {token}"}
            
            # 测试用户列表
            print("\\n4. 测试用户列表...")
            response = requests.get("http://localhost:8000/api/v1/users", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("[PASS] 用户列表测试通过")
                print(f"   用户数量: {data['data']['total']}")
            else:
                print(f"[FAIL] 用户列表测试失败: {response.status_code}")
            
            # 测试督办事项列表
            print("\\n5. 测试督办事项列表...")
            response = requests.get("http://localhost:8000/api/v1/supervision", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("[PASS] 督办事项列表测试通过")
                print(f"   督办事项数量: {data['data']['total']}")
            else:
                print(f"[FAIL] 督办事项列表测试失败: {response.status_code}")
            
            # 测试创建督办事项
            print("\\n6. 测试创建督办事项...")
            new_item = {
                "title": "快速测试督办事项",
                "content": "这是一个测试创建的督办事项",
                "type": "regular",
                "urgency": "medium",
                "deadline": "2025-08-30T23:59:59",
                "source": "快速测试"
            }
            response = requests.post("http://localhost:8000/api/v1/supervision", json=new_item, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("[PASS] 创建督办事项测试通过")
                print(f"   创建的事项ID: {data['data']['id']}")
            else:
                print(f"[FAIL] 创建督办事项测试失败: {response.status_code}")
                print(f"   响应: {response.text}")
            
        else:
            print(f"[FAIL] 登录测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
        
        print("\\nAPI测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出现异常: {e}")

if __name__ == "__main__":
    test_api()