import React, { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Layout as AntLayout, Spin } from 'antd';
import { useAppStore } from '@/store/appStore';
import Sidebar from './Sidebar';
import Header from './Header';
import Breadcrumb from './Breadcrumb';
import './Layout.css';

const { Content } = AntLayout;

const Layout: React.FC = () => {
  const { sidebarCollapsed, loading } = useAppStore();
  const location = useLocation();

  // 根据路由更新面包屑
  useEffect(() => {
    const pathMap: Record<string, string> = {
      '/dashboard': '仪表板',
      '/supervision': '督办管理',
      '/supervision/list': '督办列表',
      '/supervision/create': '创建督办',
      '/workflow': '工作流管理',
      '/analytics': '统计分析',
      '/system': '系统管理',
      '/system/users': '用户管理',
      '/system/roles': '角色管理',
      '/system/departments': '部门管理',
      '/system/settings': '系统设置',
      '/profile': '个人中心',
    };

    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbItems = pathSegments.map((segment, index) => {
      const path = '/' + pathSegments.slice(0, index + 1).join('/');
      return {
        title: pathMap[path] || segment,
        path: path,
      };
    });

    useAppStore.getState().setBreadcrumb(breadcrumbItems);
  }, [location.pathname]);

  return (
    <AntLayout className="layout">
      <Sidebar />
      <AntLayout className={`layout-main ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <Header />
        <div className="layout-content">
          <Breadcrumb />
          <Content className="content">
            <Spin spinning={loading} size="large">
              <Outlet />
            </Spin>
          </Content>
        </div>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;