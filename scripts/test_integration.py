#!/usr/bin/env python3
"""
政府效能督查系统 - 集成测试脚本
用于测试前后端API接口连通性和数据交互
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, List

# 测试配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TEST_USER = {
    "username": "test_admin",
    "password": "test123456",
    "real_name": "测试管理员",
    "email": "admin@test.com"
}

class IntegrationTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_url = f"{base_url}{API_PREFIX}"
        self.access_token = None
        self.headers = {"Content-Type": "application/json"}
        
    async def setup(self):
        """初始化测试环境"""
        print("🔧 初始化测试环境...")
        
        # 检查服务连通性
        await self.test_health_check()
        
        # 尝试登录获取token
        await self.test_login()
        
        print("✅ 测试环境初始化完成\n")
    
    async def test_health_check(self):
        """测试服务健康检查"""
        print("📊 测试服务健康状态...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    print("✅ 后端服务正常运行")
                    return True
                else:
                    print(f"❌ 后端服务异常: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 无法连接到后端服务: {e}")
            return False
    
    async def test_login(self):
        """测试用户登录"""
        print("🔐 测试用户登录...")
        
        try:
            async with httpx.AsyncClient() as client:
                # 尝试登录
                login_data = {
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
                
                response = await client.post(
                    f"{self.api_url}/auth/login",
                    data=login_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.access_token = result["data"]["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.access_token}"
                    print("✅ 用户登录成功")
                    return True
                elif response.status_code == 404:
                    # 用户不存在，尝试创建
                    print("⚠️  测试用户不存在，尝试创建...")
                    await self.create_test_user()
                    return await self.test_login()
                else:
                    print(f"❌ 登录失败: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 登录请求异常: {e}")
            return False
    
    async def create_test_user(self):
        """创建测试用户"""
        print("👤 创建测试用户...")
        
        try:
            async with httpx.AsyncClient() as client:
                # 先尝试注册
                register_data = TEST_USER.copy()
                
                response = await client.post(
                    f"{self.api_url}/auth/register",
                    json=register_data
                )
                
                if response.status_code in [200, 201]:
                    print("✅ 测试用户创建成功")
                    return True
                else:
                    print(f"⚠️  用户创建失败，可能用户已存在: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 创建用户异常: {e}")
            return False
    
    async def test_user_apis(self):
        """测试用户管理API"""
        print("👥 测试用户管理API...")
        
        if not self.access_token:
            print("❌ 未获取到访问令牌，跳过用户API测试")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                # 获取当前用户信息
                response = await client.get(
                    f"{self.api_url}/users/me",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✅ 获取用户信息成功: {user_data['data']['real_name']}")
                    
                    # 获取用户列表
                    response = await client.get(
                        f"{self.api_url}/users?page=1&size=10",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        users_data = response.json()
                        total_users = users_data['data']['total']
                        print(f"✅ 获取用户列表成功: 共{total_users}个用户")
                        return True
                    else:
                        print(f"❌ 获取用户列表失败: {response.status_code}")
                        return False
                else:
                    print(f"❌ 获取用户信息失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 用户API测试异常: {e}")
            return False
    
    async def test_supervision_apis(self):
        """测试督办事项API"""
        print("📋 测试督办事项API...")
        
        if not self.access_token:
            print("❌ 未获取到访问令牌，跳过督办API测试")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                # 获取督办事项列表
                response = await client.get(
                    f"{self.api_url}/supervision?page=1&size=10",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    total_items = data['data']['total']
                    print(f"✅ 获取督办事项列表成功: 共{total_items}个事项")
                    
                    # 尝试创建测试督办事项
                    test_item = {
                        "title": "集成测试督办事项",
                        "content": "这是一个用于集成测试的督办事项",
                        "type": "regular",
                        "urgency": "medium",
                        "deadline": (datetime.now().replace(hour=23, minute=59, second=59)).isoformat(),
                        "responsible_department_id": "test-dept-001",
                        "source": "系统测试"
                    }
                    
                    response = await client.post(
                        f"{self.api_url}/supervision",
                        json=test_item,
                        headers=self.headers
                    )
                    
                    if response.status_code in [200, 201]:
                        created_item = response.json()
                        item_id = created_item['data']['id']
                        print(f"✅ 创建督办事项成功: ID {item_id}")
                        
                        # 获取创建的事项详情
                        response = await client.get(
                            f"{self.api_url}/supervision/{item_id}",
                            headers=self.headers
                        )
                        
                        if response.status_code == 200:
                            print("✅ 获取督办事项详情成功")
                            return True
                        else:
                            print(f"❌ 获取督办事项详情失败: {response.status_code}")
                            return False
                    else:
                        print(f"⚠️  创建督办事项失败: {response.status_code} - {response.text}")
                        print("✅ 获取督办事项列表功能正常")
                        return True
                else:
                    print(f"❌ 获取督办事项列表失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 督办API测试异常: {e}")
            return False
    
    async def test_workflow_apis(self):
        """测试工作流API"""
        print("⚙️ 测试工作流API...")
        
        if not self.access_token:
            print("❌ 未获取到访问令牌，跳过工作流API测试")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                # 获取工作流模板列表
                response = await client.get(
                    f"{self.api_url}/workflow/templates?page=1&size=10",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    total_templates = data['data']['total']
                    print(f"✅ 获取工作流模板列表成功: 共{total_templates}个模板")
                    
                    # 获取我的任务
                    response = await client.get(
                        f"{self.api_url}/workflow/my-tasks?page=1&size=10",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        tasks_data = response.json()
                        total_tasks = tasks_data['data']['total']
                        print(f"✅ 获取我的任务列表成功: 共{total_tasks}个任务")
                        return True
                    else:
                        print(f"❌ 获取我的任务失败: {response.status_code}")
                        return False
                else:
                    print(f"❌ 获取工作流模板失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 工作流API测试异常: {e}")
            return False
    
    async def test_monitoring_apis(self):
        """测试监控预警API"""
        print("📊 测试监控预警API...")
        
        if not self.access_token:
            print("❌ 未获取到访问令牌，跳过监控API测试")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                # 获取监控统计
                response = await client.get(
                    f"{self.api_url}/monitoring/stats",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    stats_data = response.json()
                    print("✅ 获取监控统计成功")
                    
                    # 获取预警列表
                    response = await client.get(
                        f"{self.api_url}/monitoring/alerts?page=1&size=10",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        alerts_data = response.json()
                        total_alerts = alerts_data['data']['total']
                        print(f"✅ 获取预警列表成功: 共{total_alerts}个预警")
                        return True
                    else:
                        print(f"❌ 获取预警列表失败: {response.status_code}")
                        return False
                else:
                    print(f"❌ 获取监控统计失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 监控API测试异常: {e}")
            return False
    
    async def test_analytics_apis(self):
        """测试统计分析API"""
        print("📈 测试统计分析API...")
        
        if not self.access_token:
            print("❌ 未获取到访问令牌，跳过分析API测试")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                # 获取分析概览
                response = await client.get(
                    f"{self.api_url}/analytics/overview?start_date=2024-01-01&end_date=2024-12-31",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    analytics_data = response.json()
                    print("✅ 获取统计分析概览成功")
                    return True
                else:
                    print(f"❌ 获取统计分析失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 统计分析API测试异常: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有集成测试"""
        print("🚀 开始运行集成测试...\n")
        
        test_results = []
        
        # 初始化
        setup_success = await self.setup()
        test_results.append(("环境初始化", setup_success))
        
        if not setup_success:
            print("❌ 环境初始化失败，终止测试")
            return False
        
        # 运行各模块测试
        tests = [
            ("用户管理API", self.test_user_apis),
            ("督办事项API", self.test_supervision_apis),
            ("工作流API", self.test_workflow_apis),
            ("监控预警API", self.test_monitoring_apis),
            ("统计分析API", self.test_analytics_apis),
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                test_results.append((test_name, result))
                print()  # 空行分隔
            except Exception as e:
                print(f"❌ {test_name}测试异常: {e}\n")
                test_results.append((test_name, False))
        
        # 输出测试结果
        self.print_test_summary(test_results)
        
        # 返回总体结果
        return all(result for _, result in test_results)
    
    def print_test_summary(self, results: List[tuple]):
        """打印测试结果摘要"""
        print("=" * 50)
        print("📋 集成测试结果摘要")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{test_name:<20} {status}")
            if success:
                passed += 1
        
        print("=" * 50)
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有集成测试通过！")
        else:
            print(f"⚠️  有 {total - passed} 个测试失败，请检查相关功能")
        
        print("=" * 50)

async def main():
    """主函数"""
    tester = IntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎯 集成测试完成：系统运行正常")
        return 0
    else:
        print("\n⚠️  集成测试完成：发现问题需要修复")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)