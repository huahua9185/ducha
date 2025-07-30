import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  FileTextOutlined,
  ApartmentOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  BellOutlined,
  MonitorOutlined,
  TeamOutlined,
  BankOutlined
} from '@ant-design/icons';
import { useAppStore } from '@/store/appStore';
import { MenuItem } from '@/types';

const { Sider } = Layout;

const menuItems: MenuItem[] = [
  {
    key: '/dashboard',
    label: '仪表板',
    icon: <DashboardOutlined />,
    path: '/dashboard'
  },
  {
    key: 'supervision',
    label: '督办管理',
    icon: <FileTextOutlined />,
    children: [
      {
        key: '/supervision/list',
        label: '督办列表',
        path: '/supervision/list'
      },
      {
        key: '/supervision/create',
        label: '创建督办',
        path: '/supervision/create'
      },
      {
        key: '/supervision/urgent',
        label: '紧急督办',
        path: '/supervision/urgent'
      },
      {
        key: '/supervision/overdue',
        label: '逾期督办',
        path: '/supervision/overdue'
      }
    ]
  },
  {
    key: 'workflow',
    label: '工作流管理',
    icon: <ApartmentOutlined />,
    children: [
      {
        key: '/workflow/templates',
        label: '流程模板',
        path: '/workflow/templates'
      },
      {
        key: '/workflow/instances',
        label: '流程实例',
        path: '/workflow/instances'
      },
      {
        key: '/workflow/my-tasks',
        label: '我的任务',
        path: '/workflow/my-tasks'
      }
    ]
  },
  {
    key: 'monitoring',
    label: '监控预警',
    icon: <MonitorOutlined />,
    children: [
      {
        key: '/monitoring/dashboard',
        label: '监控概览',
        path: '/monitoring/dashboard'
      },
      {
        key: '/monitoring/alerts',
        label: '预警中心',
        path: '/monitoring/alerts'
      },
      {
        key: '/monitoring/reports',
        label: '监控报告',
        path: '/monitoring/reports'
      }
    ]
  },
  {
    key: 'analytics',
    label: '统计分析',
    icon: <BarChartOutlined />,
    children: [
      {
        key: '/analytics/overview',
        label: '统计概览',
        path: '/analytics/overview'
      },
      {
        key: '/analytics/efficiency',
        label: '效能分析',
        path: '/analytics/efficiency'
      },
      {
        key: '/analytics/department',
        label: '部门分析',
        path: '/analytics/department'
      },
      {
        key: '/analytics/reports',
        label: '统计报表',
        path: '/analytics/reports'
      }
    ]
  },
  {
    key: 'system',
    label: '系统管理',
    icon: <SettingOutlined />,
    children: [
      {
        key: '/system/users',
        label: '用户管理',
        path: '/system/users'
      },
      {
        key: '/system/roles',
        label: '角色管理',
        path: '/system/roles'
      },
      {
        key: '/system/departments',
        label: '部门管理',
        path: '/system/departments'
      },
      {
        key: '/system/permissions',
        label: '权限管理',
        path: '/system/permissions'
      },
      {
        key: '/system/settings',
        label: '系统设置',
        path: '/system/settings'
      },
      {
        key: '/system/logs',
        label: '操作日志',
        path: '/system/logs'
      }
    ]
  }
];

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarCollapsed } = useAppStore();

  // 处理菜单点击
  const handleMenuClick = ({ key }: { key: string }) => {
    // 查找对应的菜单项
    const findMenuItem = (items: MenuItem[], targetKey: string): MenuItem | null => {
      for (const item of items) {
        if (item.key === targetKey) {
          return item;
        }
        if (item.children) {
          const found = findMenuItem(item.children, targetKey);
          if (found) return found;
        }
      }
      return null;
    };

    const menuItem = findMenuItem(menuItems, key);
    if (menuItem?.path) {
      navigate(menuItem.path);
    }
  };

  // 获取当前选中的菜单项
  const getSelectedKeys = () => {
    const currentPath = location.pathname;
    
    // 精确匹配
    for (const item of menuItems) {
      if (item.path === currentPath) {
        return [item.key];
      }
      if (item.children) {
        for (const child of item.children) {
          if (child.path === currentPath) {
            return [child.key];
          }
        }
      }
    }
    
    // 部分匹配（用于默认选中）
    if (currentPath.startsWith('/supervision')) {
      return ['/supervision/list'];
    } else if (currentPath.startsWith('/workflow')) {
      return ['/workflow/templates'];
    } else if (currentPath.startsWith('/monitoring')) {
      return ['/monitoring/dashboard'];
    } else if (currentPath.startsWith('/analytics')) {
      return ['/analytics/overview'];
    } else if (currentPath.startsWith('/system')) {
      return ['/system/users'];
    }
    
    return ['/dashboard'];
  };

  // 获取展开的菜单项
  const getOpenKeys = () => {
    const currentPath = location.pathname;
    const openKeys: string[] = [];
    
    if (currentPath.startsWith('/supervision')) {
      openKeys.push('supervision');
    } else if (currentPath.startsWith('/workflow')) {
      openKeys.push('workflow');
    } else if (currentPath.startsWith('/monitoring')) {
      openKeys.push('monitoring');
    } else if (currentPath.startsWith('/analytics')) {
      openKeys.push('analytics');
    } else if (currentPath.startsWith('/system')) {
      openKeys.push('system');
    }
    
    return openKeys;
  };

  // 转换菜单数据格式
  const convertMenuItems = (items: MenuItem[]): any[] => {
    return items.map(item => ({
      key: item.key,
      icon: item.icon,
      label: item.label,
      children: item.children ? convertMenuItems(item.children) : undefined
    }));
  };

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={sidebarCollapsed}
      width={200}
      style={{
        position: 'fixed',
        height: '100vh',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 100,
        background: '#001529'
      }}
    >
      {/* Logo区域 */}
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#002140',
          color: '#fff',
          fontSize: sidebarCollapsed ? 16 : 18,
          fontWeight: 'bold'
        }}
      >
        {sidebarCollapsed ? '督查' : '政府效能督查系统'}
      </div>

      {/* 菜单 */}
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={getSelectedKeys()}
        defaultOpenKeys={getOpenKeys()}
        items={convertMenuItems(menuItems)}
        onClick={handleMenuClick}
        style={{ borderRight: 0, height: 'calc(100vh - 64px)', overflow: 'auto' }}
      />
    </Sider>
  );
};

export default Sidebar;