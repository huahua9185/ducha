#!/usr/bin/env python3
"""
前端API集成测试脚本
模拟前端JavaScript的API调用测试
"""

import requests
import json
import time
from datetime import datetime

class FrontendAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.access_token = None
        self.test_results = []
        
    def log_result(self, section, test_name, success, message="", data=None):
        """记录测试结果"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "PASS" if success else "FAIL"
        
        result = {
            "timestamp": timestamp,
            "section": section,
            "test_name": test_name,
            "success": success,
            "message": message,
            "data": data
        }
        
        self.test_results.append(result)
        
        print(f"[{timestamp}] [{status}] {section} - {test_name}")
        if message:
            print(f"    {message}")
        if data and isinstance(data, dict):
            print(f"    数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print()
    
    def make_request(self, url, method="GET", data=None, headers=None):
        """发送HTTP请求"""
        try:
            request_headers = {
                "Content-Type": "application/json"
            }
            
            if self.access_token:
                request_headers["Authorization"] = f"Bearer {self.access_token}"
                
            if headers:
                request_headers.update(headers)
            
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=request_headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=request_headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=request_headers, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "data": response.json() if response.content else None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "响应不是有效的JSON格式"
            }
    
    def test_connectivity(self):
        """测试连通性"""
        print("=== 连通性测试 ===")
        
        # 健康检查测试
        result = self.make_request(f"{self.base_url}/health")
        if result["success"]:
            self.log_result("connectivity", "健康检查", True, "服务正常运行", result["data"])
        else:
            self.log_result("connectivity", "健康检查", False, f"连接失败: {result.get('error', result.get('status_code'))}")
        
        # Ping测试
        result = self.make_request(f"{self.api_url}/ping")
        if result["success"]:
            self.log_result("connectivity", "Ping测试", True, "连通性正常", result["data"])
        else:
            self.log_result("connectivity", "Ping测试", False, f"请求失败: {result.get('error', result.get('status_code'))}")
    
    def test_authentication(self):
        """测试认证功能"""
        print("=== 认证测试 ===")
        
        # 登录测试
        login_data = {
            "username": "test_admin",
            "password": "test123456"
        }
        
        result = self.make_request(f"{self.api_url}/auth/login", "POST", login_data)
        if result["success"] and result["data"]["data"]["access_token"]:
            self.access_token = result["data"]["data"]["access_token"]
            user_info = result["data"]["data"]["user"]
            self.log_result("auth", "用户登录", True, "登录成功，已获取token", {
                "user": user_info,
                "token": self.access_token[:20] + "..."
            })
        else:
            self.log_result("auth", "用户登录", False, f"登录失败: {result.get('error', result.get('status_code'))}")
            return
        
        # 获取当前用户测试
        result = self.make_request(f"{self.api_url}/users/me")
        if result["success"]:
            self.log_result("auth", "获取当前用户", True, "成功获取用户信息", result["data"]["data"])
        else:
            self.log_result("auth", "获取当前用户", False, f"请求失败: {result.get('error', result.get('status_code'))}")
    
    def test_supervision_apis(self):
        """测试督办事项API"""
        print("=== 督办事项API测试 ===")
        
        # 获取督办事项列表
        result = self.make_request(f"{self.api_url}/supervision?page=1&size=10")
        if result["success"]:
            total = result["data"]["data"]["total"]
            items_count = len(result["data"]["data"]["items"])
            self.log_result("supervision", "获取督办列表", True, f"成功获取 {total} 个督办事项", {
                "total": total,
                "items": items_count
            })
        else:
            self.log_result("supervision", "获取督办列表", False, f"请求失败: {result.get('error', result.get('status_code'))}")
        
        # 创建督办事项
        new_item = {
            "title": "前端API集成测试督办事项",
            "content": "这是通过Python脚本模拟前端API调用创建的测试督办事项",
            "type": "regular",
            "urgency": "medium",
            "deadline": "2025-08-30T23:59:59",
            "source": "前端API集成测试"
        }
        
        result = self.make_request(f"{self.api_url}/supervision", "POST", new_item)
        if result["success"]:
            item_id = result["data"]["data"]["id"]
            self.log_result("supervision", "创建督办事项", True, f"成功创建事项，ID: {item_id}", result["data"]["data"])
            
            # 获取创建的督办事项详情
            detail_result = self.make_request(f"{self.api_url}/supervision/{item_id}")
            if detail_result["success"]:
                self.log_result("supervision", "获取督办详情", True, f"成功获取事项详情，ID: {item_id}", detail_result["data"]["data"])
            else:
                self.log_result("supervision", "获取督办详情", False, f"请求失败: {detail_result.get('error', detail_result.get('status_code'))}")
        else:
            self.log_result("supervision", "创建督办事项", False, f"创建失败: {result.get('error', result.get('status_code'))}")
    
    def test_workflow_apis(self):
        """测试工作流API"""
        print("=== 工作流API测试 ===")
        
        # 获取工作流模板
        result = self.make_request(f"{self.api_url}/workflow/templates?page=1&size=10")
        if result["success"]:
            total = result["data"]["data"]["total"]
            items_count = len(result["data"]["data"]["items"])
            self.log_result("workflow", "工作流模板", True, f"成功获取 {total} 个模板", {
                "total": total,
                "items": items_count
            })
        else:
            self.log_result("workflow", "工作流模板", False, f"请求失败: {result.get('error', result.get('status_code'))}")
        
        # 获取我的任务
        result = self.make_request(f"{self.api_url}/workflow/my-tasks?page=1&size=10")
        if result["success"]:
            total = result["data"]["data"]["total"]
            items_count = len(result["data"]["data"]["items"])
            self.log_result("workflow", "我的任务", True, f"成功获取 {total} 个任务", {
                "total": total,
                "items": items_count
            })
        else:
            self.log_result("workflow", "我的任务", False, f"请求失败: {result.get('error', result.get('status_code'))}")
    
    def test_monitoring_apis(self):
        """测试监控分析API"""
        print("=== 监控分析API测试 ===")
        
        # 监控统计
        result = self.make_request(f"{self.api_url}/monitoring/stats")
        if result["success"]:
            self.log_result("monitoring", "监控统计", True, "成功获取监控统计数据", result["data"]["data"])
        else:
            self.log_result("monitoring", "监控统计", False, f"请求失败: {result.get('error', result.get('status_code'))}")
        
        # 分析概览
        result = self.make_request(f"{self.api_url}/analytics/overview?start_date=2025-01-01&end_date=2025-12-31")
        if result["success"]:
            self.log_result("monitoring", "分析概览", True, "成功获取分析概览数据", result["data"]["data"])
        else:
            self.log_result("monitoring", "分析概览", False, f"请求失败: {result.get('error', result.get('status_code'))}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始前端API集成测试...")
        print("=" * 60)
        
        # 运行各个测试模块
        self.test_connectivity()
        time.sleep(0.5)
        
        self.test_authentication()
        time.sleep(0.5)
        
        self.test_supervision_apis()
        time.sleep(0.5)
        
        self.test_workflow_apis()
        time.sleep(0.5)
        
        self.test_monitoring_apis()
        
        # 输出测试结果统计
        self.print_summary()
    
    def print_summary(self):
        """输出测试摘要"""
        print("=" * 60)
        print("前端API集成测试结果摘要")
        print("=" * 60)
        
        # 按模块统计
        sections = {}
        for result in self.test_results:
            section = result["section"]
            if section not in sections:
                sections[section] = {"total": 0, "passed": 0}
            sections[section]["total"] += 1
            if result["success"]:
                sections[section]["passed"] += 1
        
        for section, stats in sections.items():
            success_rate = round(stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"{section:15} {stats['passed']:2}/{stats['total']:2} 通过 ({success_rate:3}%)")
        
        print("-" * 60)
        
        # 总体统计
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        overall_success_rate = round(passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总计测试: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {overall_success_rate}%")
        
        print("=" * 60)
        
        if failed_tests == 0:
            print("🎉 所有前端API集成测试通过！")
        else:
            print(f"⚠️  有 {failed_tests} 个测试失败，请检查相关功能")
        
        return failed_tests == 0

def main():
    """主函数"""
    tester = FrontendAPITester()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\\n程序退出码: {exit_code}")
    exit(exit_code)