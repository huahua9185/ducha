import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Alert,
  Table,
  Tag,
  Progress,
  Button,
  Select,
  DatePicker,
  Space,
  Badge,
  Tooltip,
  Typography,
  Spin
} from 'antd';
import {
  WarningOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  FireOutlined,
  EyeOutlined,
  ReloadOutlined,
  BellOutlined,
  RiseOutlined,
  AlertOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { monitoringService } from '@/services/monitoringService';
import './MonitoringDashboard.css';

const { RangePicker } = DatePicker;
const { Title, Text } = Typography;

interface MonitoringAlert {
  id: number;
  supervision_item_id: number;
  alert_type: 'overdue' | 'deadline_approaching' | 'slow_progress' | 'high_workload' | 'quality_issue';
  alert_level: 'normal' | 'attention' | 'warning' | 'critical';
  title: string;
  message: string;
  created_at: string;
  is_resolved: boolean;
  supervision_item: {
    id: number;
    title: string;
    number: string;
    status: string;
    deadline: string;
  };
}

const MonitoringDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [alertLevel, setAlertLevel] = useState<string>('all');
  const [alertType, setAlertType] = useState<string>('all');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);

  // 获取监控统计数据
  const { data: statsData, isLoading: statsLoading, refetch: refetchStats } = useQuery(
    ['monitoring-stats'],
    () => monitoringService.getMonitoringStats(),
    {
      refetchInterval: 30000 // 每30秒刷新一次
    }
  );

  // 获取预警列表
  const { data: alertsData, isLoading: alertsLoading, refetch: refetchAlerts } = useQuery(
    ['monitoring-alerts', alertLevel, alertType, dateRange],
    () => monitoringService.getAlerts({
      level: alertLevel === 'all' ? undefined : alertLevel,
      type: alertType === 'all' ? undefined : alertType,
      start_date: dateRange?.[0]?.format('YYYY-MM-DD'),
      end_date: dateRange?.[1]?.format('YYYY-MM-DD'),
      page: 1,
      size: 50
    }),
    {
      refetchInterval: 60000 // 每分钟刷新一次
    }
  );

  const stats = statsData?.data || {
    total_alerts: 0,
    critical_alerts: 0,
    warning_alerts: 0,
    attention_alerts: 0,
    overdue_items: 0,
    approaching_deadline_items: 0,
    slow_progress_items: 0,
    high_workload_items: 0
  };

  const alerts: MonitoringAlert[] = alertsData?.data?.items || [];

  // 获取预警级别配置
  const getAlertLevelConfig = (level: string) => {
    const configs = {
      normal: { color: 'default', text: '正常', icon: null },
      attention: { color: 'blue', text: '关注', icon: <BellOutlined /> },
      warning: { color: 'warning', text: '警告', icon: <WarningOutlined /> },
      critical: { color: 'error', text: '严重', icon: <AlertOutlined /> }
    };
    return configs[level as keyof typeof configs] || configs.normal;
  };

  // 获取预警类型配置
  const getAlertTypeConfig = (type: string) => {
    const configs = {
      overdue: { text: '逾期', color: 'red', icon: <ExclamationCircleOutlined /> },
      deadline_approaching: { text: '临近截止', color: 'orange', icon: <ClockCircleOutlined /> },
      slow_progress: { text: '进度缓慢', color: 'yellow', icon: <RiseOutlined /> },
      high_workload: { text: '工作量大', color: 'purple', icon: <FireOutlined /> },
      quality_issue: { text: '质量问题', color: 'red', icon: <WarningOutlined /> }
    };
    return configs[type as keyof typeof configs] || { text: type, color: 'default', icon: null };
  };

  // 预警表格列
  const alertColumns = [
    {
      title: '预警级别',
      dataIndex: 'alert_level',
      key: 'alert_level',
      width: 100,
      render: (level: string) => {
        const config = getAlertLevelConfig(level);
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: '预警类型',
      dataIndex: 'alert_type',
      key: 'alert_type',
      width: 120,
      render: (type: string) => {
        const config = getAlertTypeConfig(type);
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: '督办事项',
      dataIndex: 'supervision_item',
      key: 'supervision_item',
      render: (item: any) => (
        <div>
          <Button 
            type="link" 
            size="small"
            onClick={() => navigate(`/supervision/detail/${item.id}`)}
            style={{ padding: 0, fontSize: 13 }}
          >
            {item.number}
          </Button>
          <div style={{ fontSize: 12, color: '#666', marginTop: 2 }}>
            {item.title.length > 30 ? `${item.title.substring(0, 30)}...` : item.title}
          </div>
        </div>
      )
    },
    {
      title: '预警信息',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true
    },
    {
      title: '状态',
      dataIndex: 'is_resolved',
      key: 'is_resolved',
      width: 80,
      render: (resolved: boolean) => (
        <Badge 
          status={resolved ? 'success' : 'error'} 
          text={resolved ? '已处理' : '待处理'} 
        />
      )
    },
    {
      title: '预警时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm')
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: MonitoringAlert) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/supervision/detail/${record.supervision_item_id}`)}
            />
          </Tooltip>
          {!record.is_resolved && (
            <Tooltip title="标记为已处理">
              <Button
                type="text"
                size="small"
                onClick={() => {
                  // TODO: 实现标记为已处理的功能
                  console.log('标记预警为已处理:', record.id);
                }}
              >
                处理
              </Button>
            </Tooltip>
          )}
        </Space>
      )
    }
  ];

  return (
    <div className="monitoring-dashboard">
      <div className="monitoring-header">
        <Title level={3}>监控预警中心</Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => {
            refetchStats();
            refetchAlerts();
          }}>
            刷新数据
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总预警数"
              value={stats.total_alerts}
              prefix={<BellOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="严重预警"
              value={stats.critical_alerts}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="警告预警"
              value={stats.warning_alerts}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="关注预警"
              value={stats.attention_alerts}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 风险指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="风险指标概览">
            <Row gutter={16}>
              <Col xs={24} sm={12} lg={6}>
                <div className="risk-indicator">
                  <div className="risk-value">{stats.overdue_items}</div>
                  <div className="risk-label">逾期事项</div>
                  <div className="risk-icon" style={{ color: '#ff4d4f' }}>
                    <ExclamationCircleOutlined />
                  </div>
                </div>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <div className="risk-indicator">
                  <div className="risk-value">{stats.approaching_deadline_items}</div>
                  <div className="risk-label">临近截止</div>
                  <div className="risk-icon" style={{ color: '#faad14' }}>
                    <ClockCircleOutlined />
                  </div>
                </div>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <div className="risk-indicator">
                  <div className="risk-value">{stats.slow_progress_items}</div>
                  <div className="risk-label">进度缓慢</div>
                  <div className="risk-icon" style={{ color: '#1890ff' }}>
                    <RiseOutlined />
                  </div>
                </div>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <div className="risk-indicator">
                  <div className="risk-value">{stats.high_workload_items}</div>
                  <div className="risk-label">工作量大</div>
                  <div className="risk-icon" style={{ color: '#722ed1' }}>
                    <FireOutlined />
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 严重预警提醒 */}
      {stats.critical_alerts > 0 && (
        <Alert
          message="严重预警"
          description={`当前有 ${stats.critical_alerts} 个严重预警需要立即处理，请及时关注！`}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          action={
            <Button size="small" danger onClick={() => setAlertLevel('critical')}>
              查看详情
            </Button>
          }
        />
      )}

      {/* 预警列表 */}
      <Card
        title="预警列表"
        extra={
          <Space>
            <Select
              value={alertLevel}
              onChange={setAlertLevel}
              style={{ width: 120 }}
              placeholder="预警级别"
            >
              <Select.Option value="all">全部级别</Select.Option>
              <Select.Option value="critical">严重</Select.Option>
              <Select.Option value="warning">警告</Select.Option>
              <Select.Option value="attention">关注</Select.Option>
            </Select>
            
            <Select
              value={alertType}
              onChange={setAlertType}
              style={{ width: 120 }}
              placeholder="预警类型"
            >
              <Select.Option value="all">全部类型</Select.Option>
              <Select.Option value="overdue">逾期</Select.Option>
              <Select.Option value="deadline_approaching">临近截止</Select.Option>
              <Select.Option value="slow_progress">进度缓慢</Select.Option>
              <Select.Option value="high_workload">工作量大</Select.Option>
            </Select>
            
            <RangePicker
              value={dateRange}
              onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs] | null)}
              placeholder={['开始时间', '结束时间']}
            />
          </Space>
        }
      >
        <Spin spinning={alertsLoading || statsLoading}>
          <Table
            columns={alertColumns}
            dataSource={alerts}
            rowKey="id"
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
            }}
            rowClassName={(record: MonitoringAlert) => {
              if (record.alert_level === 'critical') return 'alert-row-critical';
              if (record.alert_level === 'warning') return 'alert-row-warning';
              return '';
            }}
          />
        </Spin>
      </Card>

      {/* 数据更新时间 */}
      <div style={{ textAlign: 'center', marginTop: 16, color: '#666', fontSize: 12 }}>
        数据更新时间: {new Date().toLocaleString()}
      </div>
    </div>
  );
};

export default MonitoringDashboard;