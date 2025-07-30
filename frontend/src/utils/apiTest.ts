/**
 * 前端API连接测试工具
 * 用于测试前端与后端API的连通性
 */

import { authService } from '@/services/authService';
import { supervisionService } from '@/services/supervisionService';
import { workflowService } from '@/services/workflowService';
import { monitoringService } from '@/services/monitoringService';
import { analyticsService } from '@/services/analyticsService';
import { userService } from '@/services/userService';

interface TestResult {
  name: string;
  status: 'success' | 'error' | 'warning';
  message: string;
  duration?: number;
}

class ApiTester {
  private results: TestResult[] = [];

  // 添加测试结果
  private addResult(name: string, status: 'success' | 'error' | 'warning', message: string, duration?: number) {
    this.results.push({ name, status, message, duration });
    
    const statusIcon = status === 'success' ? '✅' : status === 'error' ? '❌' : '⚠️';
    const durationText = duration ? ` (${duration}ms)` : '';
    console.log(`${statusIcon} ${name}: ${message}${durationText}`);
  }

  // 测试API端点连通性
  private async testEndpoint(name: string, testFunc: () => Promise<any>): Promise<boolean> {
    const startTime = Date.now();
    
    try {
      await testFunc();
      const duration = Date.now() - startTime;
      this.addResult(name, 'success', '连接成功', duration);
      return true;
    } catch (error: any) {
      const duration = Date.now() - startTime;
      const message = error.response?.data?.detail || error.message || '连接失败';
      this.addResult(name, 'error', message, duration);
      return false;
    }
  }

  // 测试用户认证API
  async testAuthApis(): Promise<boolean> {
    console.log('🔐 测试用户认证API...');
    
    let success = true;

    // 测试登录接口（模拟错误请求）
    const loginSuccess = await this.testEndpoint('登录接口', async () => {
      try {
        await authService.login({ username: 'test_user', password: 'wrong_password' });
      } catch (error: any) {
        // 预期的错误（用户不存在或密码错误）
        if (error.response?.status === 401 || error.response?.status === 404) {
          return Promise.resolve(); // 接口可达，返回预期错误
        }
        throw error; // 其他错误继续抛出
      }
    });

    return loginSuccess;
  }

  // 测试用户管理API
  async testUserApis(): Promise<boolean> {
    console.log('👥 测试用户管理API...');
    
    // 注意：这些测试需要有效的认证token
    const testCases = [
      {
        name: '获取用户列表',
        test: () => userService.getUsers({ page: 1, size: 10 })
      }
    ];

    let allSuccess = true;
    for (const testCase of testCases) {
      const success = await this.testEndpoint(testCase.name, testCase.test);
      if (!success) allSuccess = false;
    }

    return allSuccess;
  }

  // 测试督办事项API
  async testSupervisionApis(): Promise<boolean> {
    console.log('📋 测试督办事项API...');
    
    const testCases = [
      {
        name: '获取督办事项列表',
        test: () => supervisionService.getSupervisionItems({ page: 1, size: 10 })
      },
      {
        name: '获取督办统计',
        test: () => supervisionService.getSupervisionStats()
      }
    ];

    let allSuccess = true;
    for (const testCase of testCases) {
      const success = await this.testEndpoint(testCase.name, testCase.test);
      if (!success) allSuccess = false;
    }

    return allSuccess;
  }

  // 测试工作流API
  async testWorkflowApis(): Promise<boolean> {
    console.log('⚙️ 测试工作流API...');
    
    const testCases = [
      {
        name: '获取工作流模板',
        test: () => workflowService.getTemplateList({ page: 1, size: 10 })
      },
      {
        name: '获取工作流实例',
        test: () => workflowService.getInstanceList({ page: 1, size: 10 })
      },
      {
        name: '获取我的任务',
        test: () => workflowService.getMyTasks({ page: 1, size: 10 })
      }
    ];

    let allSuccess = true;
    for (const testCase of testCases) {
      const success = await this.testEndpoint(testCase.name, testCase.test);
      if (!success) allSuccess = false;
    }

    return allSuccess;
  }

  // 测试监控预警API
  async testMonitoringApis(): Promise<boolean> {
    console.log('📊 测试监控预警API...');
    
    const testCases = [
      {
        name: '获取监控统计',
        test: () => monitoringService.getMonitoringStats()
      },
      {
        name: '获取预警列表',
        test: () => monitoringService.getAlerts({ page: 1, size: 10 })
      }
    ];

    let allSuccess = true;
    for (const testCase of testCases) {
      const success = await this.testEndpoint(testCase.name, testCase.test);
      if (!success) allSuccess = false;
    }

    return allSuccess;
  }

  // 测试统计分析API
  async testAnalyticsApis(): Promise<boolean> {
    console.log('📈 测试统计分析API...');
    
    const testCases = [
      {
        name: '获取分析概览',
        test: () => analyticsService.getAnalyticsOverview({
          start_date: '2024-01-01',
          end_date: '2024-12-31'
        })
      }
    ];

    let allSuccess = true;
    for (const testCase of testCases) {
      const success = await this.testEndpoint(testCase.name, testCase.test);
      if (!success) allSuccess = false;
    }

    return allSuccess;
  }

  // 运行所有API测试
  async runAllTests(): Promise<TestResult[]> {
    console.log('🚀 开始前端API连通性测试...\n');
    
    this.results = []; // 重置结果

    // 运行各模块测试
    const tests = [
      { name: '用户认证', test: () => this.testAuthApis() },
      { name: '用户管理', test: () => this.testUserApis() },
      { name: '督办事项', test: () => this.testSupervisionApis() },
      { name: '工作流管理', test: () => this.testWorkflowApis() },
      { name: '监控预警', test: () => this.testMonitoringApis() },
      { name: '统计分析', test: () => this.testAnalyticsApis() }
    ];

    for (const { name, test } of tests) {
      try {
        console.log(`\n--- ${name} ---`);
        await test();
      } catch (error) {
        console.error(`${name}测试异常:`, error);
        this.addResult(name, 'error', '测试异常');
      }
    }

    this.printSummary();
    return this.results;
  }

  // 打印测试摘要
  private printSummary() {
    console.log('\n' + '='.repeat(50));
    console.log('📋 前端API测试结果摘要');
    console.log('='.repeat(50));
    
    const successful = this.results.filter(r => r.status === 'success').length;
    const failed = this.results.filter(r => r.status === 'error').length;
    const warnings = this.results.filter(r => r.status === 'warning').length;
    
    console.log(`✅ 成功: ${successful}`);
    console.log(`❌ 失败: ${failed}`);
    console.log(`⚠️  警告: ${warnings}`);
    console.log(`📊 总计: ${this.results.length}`);
    
    if (failed === 0) {
      console.log('\n🎉 所有API测试通过！');
    } else {
      console.log(`\n⚠️  有 ${failed} 个API测试失败，请检查后端服务`);
    }
    
    console.log('='.repeat(50));
  }

  // 获取测试结果
  getResults(): TestResult[] {
    return this.results;
  }
}

// 导出测试工具
export const apiTester = new ApiTester();

// 在开发环境下可以在控制台中调用
if (process.env.NODE_ENV === 'development') {
  // @ts-ignore
  window.apiTester = apiTester;
  console.log('🔧 API测试工具已加载到全局，可在控制台中使用 apiTester.runAllTests()');
}

export default ApiTester;