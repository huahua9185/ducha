#!/usr/bin/env python3
"""
简化集成测试脚本
测试前后端API连通性
"""

import httpx
import asyncio
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

class SimpleIntegrationTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_url = f"{base_url}{API_PREFIX}"
        self.access_token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        
    def add_result(self, name: str, success: bool, message: str = ""):
        status = "PASS" if success else "FAIL"
        self.test_results.append((name, success, message))
        print(f"[{status}] {name}: {message}")
    
    async def test_health_check(self):
        """测试服务健康检查"""
        print("=== 测试服务健康状态 ===")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.add_result("健康检查", True, "服务正常运行")
                    return True
                else:
                    self.add_result("健康检查", False, f"状态码: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.add_result("健康检查", False, f"连接失败: {e}")
            return False
    
    async def test_ping(self):
        """测试ping端点"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/ping")
                
                if response.status_code == 200:
                    data = response.json()
                    self.add_result("Ping测试", True, "连通性正常")
                    return True
                else:
                    self.add_result("Ping测试", False, f"状态码: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.add_result("Ping测试", False, f"请求失败: {e}")
            return False
    
    async def test_login(self):
        """测试用户登录"""
        print("\\n=== 测试用户认证 ===")
        
        try:
            async with httpx.AsyncClient() as client:
                login_data = {
                    "username": "test_admin",
                    "password": "test123456"
                }
                
                response = await client.post(
                    f"{self.api_url}/auth/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "data" in result and "access_token" in result["data"]:
                        self.access_token = result["data"]["access_token"]
                        self.headers["Authorization"] = f"Bearer {self.access_token}"
                        self.add_result("用户登录", True, "登录成功，获取到token")
                        return True
                    else:
                        self.add_result("用户登录", False, "响应格式错误")
                        return False
                else:
                    self.add_result("用户登录", False, f"状态码: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.add_result("用户登录", False, f"请求异常: {e}")
            return False
    
    async def test_user_apis(self):
        """测试用户管理API"""
        print("\\n=== 测试用户管理API ===")
        
        # 测试获取当前用户信息
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/users/me",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    self.add_result("获取当前用户", True, "成功获取用户信息")
                else:
                    self.add_result("获取当前用户", False, f"状态码: {response.status_code}")
                    
        except Exception as e:
            self.add_result("获取当前用户", False, f"请求异常: {e}")
        
        # 测试获取用户列表
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/users?page=1&size=10",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data and "items" in data["data"]:
                        total = data["data"]["total"]
                        self.add_result("获取用户列表", True, f"成功获取{total}个用户")
                    else:
                        self.add_result("获取用户列表", False, "响应格式错误")
                else:
                    self.add_result("获取用户列表", False, f"状态码: {response.status_code}")
                    
        except Exception as e:
            self.add_result("获取用户列表", False, f"请求异常: {e}")
    
    async def test_supervision_apis(self):
        """测试督办事项API"""
        print("\\n=== 测试督办事项API ===")
        
        # 测试获取督办事项列表
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/supervision?page=1&size=10",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data and "items" in data["data"]:
                        total = data["data"]["total"]
                        self.add_result("获取督办列表", True, f"成功获取{total}个督办事项")
                    else:
                        self.add_result("获取督办列表", False, "响应格式错误")
                else:
                    self.add_result("获取督办列表", False, f"状态码: {response.status_code}")
                    
        except Exception as e:
            self.add_result("获取督办列表", False, f"请求异常: {e}")
        
        # 测试创建督办事项
        try:
            async with httpx.AsyncClient() as client:
                test_item = {
                    "title": "集成测试督办事项",
                    "content": "这是一个用于集成测试的督办事项",
                    "type": "regular",
                    "urgency": "medium",
                    "deadline": "2025-08-30T23:59:59",
                    "source": "系统测试"
                }
                
                response = await client.post(
                    f"{self.api_url}/supervision",
                    json=test_item,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data and "id" in data["data"]:
                        item_id = data["data"]["id"]
                        self.add_result("创建督办事项", True, f"成功创建事项，ID: {item_id}")
                        
                        # 测试获取督办事项详情
                        detail_response = await client.get(
                            f"{self.api_url}/supervision/{item_id}",
                            headers=self.headers
                        )
                        
                        if detail_response.status_code == 200:
                            self.add_result("获取督办详情", True, "成功获取事项详情")
                        else:
                            self.add_result("获取督办详情", False, f"状态码: {detail_response.status_code}")
                    else:
                        self.add_result("创建督办事项", False, "响应格式错误")
                else:
                    self.add_result("创建督办事项", False, f"状态码: {response.status_code}")
                    
        except Exception as e:
            self.add_result("创建督办事项", False, f"请求异常: {e}")
    
    async def test_workflow_apis(self):
        """测试工作流API"""
        print("\\n=== 测试工作流API ===")
        
        tests = [
            ("获取工作流模板", f"{self.api_url}/workflow/templates?page=1&size=10"),
            ("获取工作流实例", f"{self.api_url}/workflow/instances?page=1&size=10"),
            ("获取我的任务", f"{self.api_url}/workflow/my-tasks?page=1&size=10")
        ]
        
        for test_name, url in tests:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=self.headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "data" in data and "items" in data["data"]:
                            total = data["data"]["total"]
                            self.add_result(test_name, True, f"成功获取{total}个记录")
                        else:
                            self.add_result(test_name, False, "响应格式错误")
                    else:
                        self.add_result(test_name, False, f"状态码: {response.status_code}")
                        
            except Exception as e:
                self.add_result(test_name, False, f"请求异常: {e}")
    
    async def test_monitoring_apis(self):
        """测试监控预警API"""
        print("\\n=== 测试监控预警API ===")
        
        # 测试监控统计
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/monitoring/stats",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        self.add_result("获取监控统计", True, "成功获取监控数据")
                    else:
                        self.add_result("获取监控统计", False, "响应格式错误")
                else:
                    self.add_result("获取监控统计", False, f"状态码: {response.status_code}")
                    
        except Exception as e:
            self.add_result("获取监控统计", False, f"请求异常: {e}")
        
        # 测试预警列表
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/monitoring/alerts?page=1&size=10",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data and "items" in data["data"]:
                        total = data["data"]["total"]
                        self.add_result("获取预警列表", True, f"成功获取{total}个预警")
                    else:
                        self.add_result("获取预警列表", False, "响应格式错误")
                else:
                    self.add_result("获取预警列表", False, f"状态码: {response.status_code}")
                    
        except Exception as e:
            self.add_result("获取预警列表", False, f"请求异常: {e}")
    
    async def test_analytics_apis(self):
        """测试统计分析API"""
        print("\\n=== 测试统计分析API ===")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/analytics/overview?start_date=2025-01-01&end_date=2025-12-31",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        self.add_result("获取分析概览", True, "成功获取统计分析数据")
                    else:
                        self.add_result("获取分析概览", False, "响应格式错误")
                else:
                    self.add_result("获取分析概览", False, f"状态码: {response.status_code}")
                    
        except Exception as e:
            self.add_result("获取分析概览", False, f"请求异常: {e}")
    
    async def run_all_tests(self):
        """运行所有集成测试"""
        print("集成测试开始...")
        print("服务地址:", self.base_url)
        print("=" * 60)
        
        # 基础连通性测试
        health_ok = await self.test_health_check()
        if not health_ok:
            print("\\n服务未启动或不可访问，终止测试")
            return False
        
        await self.test_ping()
        
        # 认证测试
        login_ok = await self.test_login()
        if not login_ok:
            print("\\n认证失败，跳过需要认证的API测试")
        else:
            # API功能测试
            await self.test_user_apis()
            await self.test_supervision_apis()
            await self.test_workflow_apis()
            await self.test_monitoring_apis()
            await self.test_analytics_apis()
        
        # 输出测试结果
        self.print_summary()
        
        # 返回测试是否全部通过
        return all(success for _, success, _ in self.test_results)
    
    def print_summary(self):
        """输出测试摘要"""
        print("\\n" + "=" * 60)
        print("集成测试结果摘要")
        print("=" * 60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for name, success, message in self.test_results:
            status = "PASS" if success else "FAIL"
            print(f"[{status}] {name}")
        
        print("=" * 60)
        print(f"测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("所有测试通过！")
        else:
            print(f"有 {total - passed} 个测试失败")
        
        print("=" * 60)

async def main():
    """主函数"""
    tester = SimpleIntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\\n集成测试完成：系统运行正常")
        return 0
    else:
        print("\\n集成测试完成：部分功能存在问题")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"\\n退出码: {exit_code}")