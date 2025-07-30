import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import Layout from '@/components/Layout';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import { SupervisionList, SupervisionForm, SupervisionDetail } from '@/pages/Supervision';
import { WorkflowTemplates, WorkflowInstances, MyTasks } from '@/pages/Workflow';
import MonitoringDashboard from '@/pages/Monitoring/MonitoringDashboard';
import AnalyticsOverview from '@/pages/Analytics/AnalyticsOverview';
import UserManagement from '@/pages/System/UserManagement';
import SystemSettings from '@/pages/System/SystemSettings';
import ProtectedRoute from '@/components/ProtectedRoute';

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Routes>
      {/* 登录页面 */}
      <Route 
        path="/login" 
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
        } 
      />
      
      {/* 主应用布局 */}
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        {/* 默认重定向到仪表板 */}
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        {/* 仪表板 */}
        <Route path="dashboard" element={<Dashboard />} />
        
        {/* 督办管理 */}
        <Route path="supervision">
          <Route index element={<SupervisionList />} />
          <Route path="list" element={<SupervisionList />} />
          <Route path="create" element={<SupervisionForm />} />
          <Route path="edit/:id" element={<SupervisionForm />} />
          <Route path="detail/:id" element={<SupervisionDetail />} />
          <Route path="urgent" element={<SupervisionList />} />
          <Route path="overdue" element={<SupervisionList />} />
        </Route>
        
        {/* 工作流管理 */}
        <Route path="workflow">
          <Route index element={<WorkflowTemplates />} />
          <Route path="templates" element={<WorkflowTemplates />} />
          <Route path="instances" element={<WorkflowInstances />} />
          <Route path="my-tasks" element={<MyTasks />} />
        </Route>
        
        {/* 监控预警 */}
        <Route path="monitoring">
          <Route index element={<MonitoringDashboard />} />
          <Route path="dashboard" element={<MonitoringDashboard />} />
          <Route path="alerts" element={<div>预警中心</div>} />
          <Route path="reports" element={<div>监控报告</div>} />
        </Route>
        
        {/* 统计分析 */}
        <Route path="analytics">
          <Route index element={<AnalyticsOverview />} />
          <Route path="overview" element={<AnalyticsOverview />} />
          <Route path="efficiency" element={<div>效能分析</div>} />
          <Route path="department" element={<div>部门分析</div>} />
          <Route path="reports" element={<div>统计报表</div>} />
        </Route>
        
        {/* 系统管理 */}
        <Route path="system">
          <Route index element={<UserManagement />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="roles" element={<div>角色管理</div>} />
          <Route path="departments" element={<div>部门管理</div>} />
          <Route path="permissions" element={<div>权限管理</div>} />
          <Route path="settings" element={<SystemSettings />} />
          <Route path="logs" element={<div>操作日志</div>} />
        </Route>
        
        {/* 个人中心 */}
        <Route path="profile" element={<div>个人中心</div>} />
        
        {/* 404 页面 */}
        <Route path="*" element={<div>页面不存在</div>} />
      </Route>
    </Routes>
  );
}

export default App;