import React, { useState } from 'react';
import { Layout, Button, Dropdown, Avatar, Badge, Space, Drawer, List, Typography } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useAppStore } from '@/store/appStore';
import { authService } from '@/services/authService';
import { message } from 'antd';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { sidebarCollapsed, toggleSidebar } = useAppStore();
  const [notificationDrawerVisible, setNotificationDrawerVisible] = useState(false);

  // 处理登出
  const handleLogout = async () => {
    try {
      await authService.logout();
      logout();
      message.success('退出登录成功');
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      // 即使后端退出失败，也清除本地认证信息
      logout();
      navigate('/login');
    }
  };

  // 用户菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '个人设置',
      onClick: () => navigate('/profile/settings')
    },
    {
      type: 'divider' as const
    },
    {
      key: 'help',
      icon: <QuestionCircleOutlined />,
      label: '帮助中心',
      onClick: () => window.open('/help', '_blank')
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout
    }
  ];

  // 模拟通知数据
  const notifications = [
    {
      id: '1',
      title: '督办事项逾期提醒',
      content: '您有1个督办事项已逾期，请及时处理',
      time: '5分钟前',
      type: 'warning'
    },
    {
      id: '2',
      title: '新任务分配',
      content: '您收到一个新的督办任务',
      time: '1小时前',
      type: 'info'
    },
    {
      id: '3',
      title: '系统维护通知',
      content: '系统将于今晚22:00-24:00进行维护',
      time: '2小时前',
      type: 'info'
    }
  ];

  return (
    <AntHeader
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        left: sidebarCollapsed ? 80 : 200,
        height: 64,
        padding: '0 24px',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 99,
        transition: 'left 0.2s'
      }}
    >
      {/* 左侧区域 */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Button
          type="text"
          icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={toggleSidebar}
          style={{ fontSize: 16, width: 40, height: 40 }}
        />
      </div>

      {/* 右侧区域 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* 通知 */}
        <Badge count={notifications.length} size="small">
          <Button
            type="text"
            icon={<BellOutlined style={{ fontSize: 18 }} />}
            onClick={() => setNotificationDrawerVisible(true)}
            style={{ width: 40, height: 40 }}
          />
        </Badge>

        {/* 用户信息 */}
        <Dropdown
          menu={{ items: userMenuItems }}
          placement="bottomRight"
          arrow
        >
          <Space style={{ cursor: 'pointer', padding: '0 8px' }}>
            <Avatar 
              size="small" 
              icon={<UserOutlined />} 
              src={user?.avatar_url}
            />
            <Text strong>{user?.real_name || user?.username}</Text>
          </Space>
        </Dropdown>
      </div>

      {/* 通知抽屉 */}
      <Drawer
        title="通知中心"
        placement="right"
        onClose={() => setNotificationDrawerVisible(false)}
        open={notificationDrawerVisible}
        width={400}
        extra={
          <Space>
            <Button type="link">全部已读</Button>
            <Button type="link">查看全部</Button>
          </Space>
        }
      >
        <List
          dataSource={notifications}
          renderItem={(item) => (
            <List.Item
              style={{ cursor: 'pointer', padding: '12px 0' }}
              onClick={() => {
                // 处理通知点击
                console.log('点击通知:', item);
              }}
            >
              <List.Item.Meta
                title={
                  <Text strong style={{ fontSize: 14 }}>
                    {item.title}
                  </Text>
                }
                description={
                  <div>
                    <Text type="secondary" style={{ fontSize: 13 }}>
                      {item.content}
                    </Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {item.time}
                    </Text>
                  </div>
                }
              />
            </List.Item>
          )}
          locale={{ emptyText: '暂无通知' }}
        />
      </Drawer>
    </AntHeader>
  );
};

export default Header;