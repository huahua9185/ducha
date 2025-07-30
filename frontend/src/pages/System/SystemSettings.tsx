import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Switch,
  Button,
  message,
  Divider,
  Space,
  InputNumber,
  Select,
  Row,
  Col,
  Typography,
  Alert,
  Tag
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
  SettingOutlined,
  SecurityScanOutlined,
  DatabaseOutlined,
  MailOutlined,
  BellOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import './SystemSettings.css';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface SystemConfig {
  // 基础设置
  system_name: string;
  system_description: string;
  system_version: string;
  
  // 安全设置
  password_min_length: number;
  password_complexity: boolean;
  session_timeout: number;
  max_login_attempts: number;
  
  // 邮件设置
  email_enabled: boolean;
  smtp_host: string;
  smtp_port: number;
  smtp_username: string;
  smtp_password: string;
  smtp_ssl: boolean;
  
  // 通知设置
  notification_enabled: boolean;
  notification_email: boolean;
  notification_sms: boolean;
  
  // 工作流设置
  workflow_auto_assign: boolean;
  workflow_deadline_alert: boolean;
  workflow_escalation_enabled: boolean;
  
  // 数据备份设置
  backup_enabled: boolean;
  backup_frequency: string;
  backup_retention_days: number;
}

const SystemSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');

  // 模拟当前配置数据
  const [config, setConfig] = useState<SystemConfig>({
    system_name: '政府效能督查系统',
    system_description: '基于云原生架构的政府效能督查管理平台',
    system_version: '1.0.0',
    
    password_min_length: 8,
    password_complexity: true,
    session_timeout: 120,
    max_login_attempts: 5,
    
    email_enabled: true,
    smtp_host: 'smtp.example.com',
    smtp_port: 587,
    smtp_username: 'system@example.com',
    smtp_password: '',
    smtp_ssl: true,
    
    notification_enabled: true,
    notification_email: true,
    notification_sms: false,
    
    workflow_auto_assign: true,
    workflow_deadline_alert: true,
    workflow_escalation_enabled: true,
    
    backup_enabled: true,
    backup_frequency: 'daily',
    backup_retention_days: 30
  });

  // 保存配置
  const handleSave = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      
      // 这里应该调用API保存配置
      console.log('保存系统配置:', values);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setConfig(values);
      message.success('系统配置保存成功');
    } catch (error) {
      console.error('保存配置失败:', error);
      message.error('保存失败，请检查输入');
    } finally {
      setLoading(false);
    }
  };

  // 重置配置
  const handleReset = () => {
    form.setFieldsValue(config);
    message.info('已重置为当前配置');
  };

  // 测试邮件连接
  const testEmailConnection = async () => {
    try {
      const emailConfig = form.getFieldsValue(['smtp_host', 'smtp_port', 'smtp_username', 'smtp_password']);
      console.log('测试邮件连接:', emailConfig);
      
      // 模拟测试连接
      await new Promise(resolve => setTimeout(resolve, 2000));
      message.success('邮件服务器连接测试成功');
    } catch (error) {
      message.error('邮件服务器连接测试失败');
    }
  };

  return (
    <div className="system-settings">
      <div className="settings-header">
        <Title level={3}>
          <SettingOutlined style={{ marginRight: 8 }} />
          系统设置
        </Title>
        <Text type="secondary">配置系统的基础参数和功能选项</Text>
      </div>

      <Row gutter={24}>
        {/* 设置菜单 */}
        <Col span={6}>
          <Card size="small">
            <div className="settings-menu">
              <div 
                className={`menu-item ${activeTab === 'basic' ? 'active' : ''}`}
                onClick={() => setActiveTab('basic')}
              >
                <SettingOutlined style={{ marginRight: 8 }} />
                基础设置
              </div>
              <div 
                className={`menu-item ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => setActiveTab('security')}
              >
                <SecurityScanOutlined style={{ marginRight: 8 }} />
                安全设置
              </div>
              <div 
                className={`menu-item ${activeTab === 'email' ? 'active' : ''}`}
                onClick={() => setActiveTab('email')}
              >
                <MailOutlined style={{ marginRight: 8 }} />
                邮件设置
              </div>
              <div 
                className={`menu-item ${activeTab === 'notification' ? 'active' : ''}`}
                onClick={() => setActiveTab('notification')}
              >
                <BellOutlined style={{ marginRight: 8 }} />
                通知设置
              </div>
              <div 
                className={`menu-item ${activeTab === 'workflow' ? 'active' : ''}`}
                onClick={() => setActiveTab('workflow')}
              >
                <ClockCircleOutlined style={{ marginRight: 8 }} />
                工作流设置
              </div>
              <div 
                className={`menu-item ${activeTab === 'backup' ? 'active' : ''}`}
                onClick={() => setActiveTab('backup')}
              >
                <DatabaseOutlined style={{ marginRight: 8 }} />
                备份设置
              </div>
            </div>
          </Card>
        </Col>

        {/* 设置内容 */}
        <Col span={18}>
          <Card>
            <Form
              form={form}
              layout="vertical"
              initialValues={config}
              onFinish={handleSave}
            >
              {/* 基础设置 */}
              {activeTab === 'basic' && (
                <div className="settings-content">
                  <Title level={4}>基础设置</Title>
                  <Alert
                    message="系统基础信息配置"
                    description="这些设置将影响系统的基本信息显示"
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />
                  
                  <Form.Item
                    name="system_name"
                    label="系统名称"
                    rules={[{ required: true, message: '请输入系统名称' }]}
                  >
                    <Input placeholder="请输入系统名称" />
                  </Form.Item>

                  <Form.Item
                    name="system_description"
                    label="系统描述"
                  >
                    <TextArea rows={3} placeholder="请输入系统描述" />
                  </Form.Item>

                  <Form.Item
                    name="system_version"
                    label="系统版本"
                  >
                    <Input placeholder="如: 1.0.0" />
                  </Form.Item>
                </div>
              )}

              {/* 安全设置 */}
              {activeTab === 'security' && (
                <div className="settings-content">
                  <Title level={4}>安全设置</Title>
                  <Alert
                    message="系统安全策略配置"
                    description="配置密码策略、会话管理等安全相关设置"
                    type="warning"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  <Form.Item
                    name="password_min_length"
                    label="密码最小长度"
                    rules={[{ required: true, message: '请设置密码最小长度' }]}
                  >
                    <InputNumber min={6} max={20} style={{ width: '100%' }} />
                  </Form.Item>

                  <Form.Item
                    name="password_complexity"
                    label="密码复杂度要求"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="开启" unCheckedChildren="关闭" />
                  </Form.Item>

                  <Form.Item
                    name="session_timeout"
                    label="会话超时时间（分钟）"
                    rules={[{ required: true, message: '请设置会话超时时间' }]}
                  >
                    <InputNumber min={30} max={480} style={{ width: '100%' }} />
                  </Form.Item>

                  <Form.Item
                    name="max_login_attempts"
                    label="最大登录尝试次数"
                    rules={[{ required: true, message: '请设置最大登录尝试次数' }]}
                  >
                    <InputNumber min={3} max={10} style={{ width: '100%' }} />
                  </Form.Item>
                </div>
              )}

              {/* 邮件设置 */}
              {activeTab === 'email' && (
                <div className="settings-content">
                  <Title level={4}>邮件设置</Title>
                  <Alert
                    message="邮件服务器配置"
                    description="配置SMTP服务器信息，用于发送系统通知邮件"
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  <Form.Item
                    name="email_enabled"
                    label="启用邮件服务"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>

                  <Form.Item
                    name="smtp_host"
                    label="SMTP服务器"
                    rules={[{ required: true, message: '请输入SMTP服务器地址' }]}
                  >
                    <Input placeholder="如: smtp.example.com" />
                  </Form.Item>

                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="smtp_port"
                        label="SMTP端口"
                        rules={[{ required: true, message: '请输入SMTP端口' }]}
                      >
                        <InputNumber min={1} max={65535} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="smtp_ssl"
                        label="启用SSL"
                        valuePropName="checked"
                      >
                        <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="smtp_username"
                    label="用户名"
                    rules={[{ required: true, message: '请输入SMTP用户名' }]}
                  >
                    <Input placeholder="请输入SMTP用户名" />
                  </Form.Item>

                  <Form.Item
                    name="smtp_password"
                    label="密码"
                  >
                    <Input.Password placeholder="请输入SMTP密码" />
                  </Form.Item>

                  <Form.Item>
                    <Button onClick={testEmailConnection}>
                      测试连接
                    </Button>
                  </Form.Item>
                </div>
              )}

              {/* 通知设置 */}
              {activeTab === 'notification' && (
                <div className="settings-content">
                  <Title level={4}>通知设置</Title>
                  
                  <Form.Item
                    name="notification_enabled"
                    label="启用系统通知"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>

                  <Form.Item
                    name="notification_email"
                    label="邮件通知"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>

                  <Form.Item
                    name="notification_sms"
                    label="短信通知"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>
                </div>
              )}

              {/* 工作流设置 */}
              {activeTab === 'workflow' && (
                <div className="settings-content">
                  <Title level={4}>工作流设置</Title>
                  
                  <Form.Item
                    name="workflow_auto_assign"
                    label="自动任务分配"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>

                  <Form.Item
                    name="workflow_deadline_alert"
                    label="截止时间提醒"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>

                  <Form.Item
                    name="workflow_escalation_enabled"
                    label="任务升级"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>
                </div>
              )}

              {/* 备份设置 */}
              {activeTab === 'backup' && (
                <div className="settings-content">
                  <Title level={4}>数据备份设置</Title>
                  
                  <Form.Item
                    name="backup_enabled"
                    label="启用自动备份"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                  </Form.Item>

                  <Form.Item
                    name="backup_frequency"
                    label="备份频率"
                    rules={[{ required: true, message: '请选择备份频率' }]}
                  >
                    <Select>
                      <Select.Option value="daily">每日</Select.Option>
                      <Select.Option value="weekly">每周</Select.Option>
                      <Select.Option value="monthly">每月</Select.Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    name="backup_retention_days"
                    label="备份保留天数"
                    rules={[{ required: true, message: '请设置备份保留天数' }]}
                  >
                    <InputNumber min={7} max={365} style={{ width: '100%' }} />
                  </Form.Item>
                </div>
              )}

              {/* 操作按钮 */}
              <Divider />
              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    loading={loading}
                    htmlType="submit"
                  >
                    保存配置
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={handleReset}
                  >
                    重置
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SystemSettings;