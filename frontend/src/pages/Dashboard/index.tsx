import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Alert, List, Tag, Progress, Button, Spin } from 'antd';
import {
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  TrophyOutlined,
  TeamOutlined,
  WarningOutlined,
  FireOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { supervisionService } from '@/services/supervisionService';
import { SupervisionItem } from '@/types';
import './Dashboard.css';

interface DashboardStats {
  total_count: number;
  pending_count: number;
  in_progress_count: number;
  completed_count: number;
  overdue_count: number;
  completion_rate: number;
  average_efficiency_score: number;
  urgent_count: number;
  key_count: number;
}

const Dashboard: React.FC = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<'week' | 'month' | 'quarter'>('month');

  // 获取统计数据
  const { data: stats, isLoading: statsLoading } = useQuery(
    'supervision-stats',
    () => supervisionService.getSupervisionStats(),
    {
      refetchInterval: 60000, // 每分钟刷新一次
    }
  );

  // 获取逾期事项
  const { data: overdueItems } = useQuery(
    'overdue-items',
    () => supervisionService.getOverdueItems(10),
    {
      refetchInterval: 30000, // 每30秒刷新一次
    }
  );

  // 获取紧急事项
  const { data: urgentItems } = useQuery(
    'urgent-items',
    () => supervisionService.getUrgentItems(10),
    {
      refetchInterval: 30000,
    }
  );

  const dashboardStats: DashboardStats = stats?.data || {
    total_count: 0,
    pending_count: 0,
    in_progress_count: 0,
    completed_count: 0,
    overdue_count: 0,
    completion_rate: 0,
    average_efficiency_score: 0,
    urgent_count: 0,
    key_count: 0
  };

  // 获取状态标签颜色
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'draft': 'default',
      'pending': 'blue',
      'in_progress': 'processing',
      'completed': 'success',
      'overdue': 'error',
      'suspended': 'warning',
      'cancelled': 'default'
    };
    return colors[status] || 'default';
  };

  // 获取紧急程度标签颜色
  const getUrgencyColor = (urgency: string) => {
    const colors: Record<string, string> = {
      'low': 'default',
      'medium': 'warning',
      'high': 'error'
    };
    return colors[urgency] || 'default';
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>仪表板概览</h2>
        <p>政府效能督查系统运行状态及关键指标</p>
      </div>

      {/* 关键指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="督办总数"
              value={dashboardStats.total_count}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="进行中"
              value={dashboardStats.in_progress_count}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已完成"
              value={dashboardStats.completed_count}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="逾期项目"
              value={dashboardStats.overdue_count}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 效能指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={8}>
          <Card title="完成率" size="small">
            <Progress
              type="circle"
              percent={dashboardStats.completion_rate}
              format={(percent) => `${percent?.toFixed(1)}%`}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card title="效率评分" size="small">
            <Progress
              type="circle"
              percent={dashboardStats.average_efficiency_score * 20} // 转换为百分比
              format={() => `${dashboardStats.average_efficiency_score.toFixed(1)}分`}
              strokeColor={{
                '0%': '#ff4d4f',
                '50%': '#faad14',
                '100%': '#52c41a',
              }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card title="重点督办" size="small">
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <div style={{ fontSize: 32, fontWeight: 'bold', color: '#fa8c16' }}>
                <TrophyOutlined style={{ marginRight: 8 }} />
                {dashboardStats.key_count}
              </div>
              <div style={{ color: '#666', marginTop: 8 }}>
                项重点督办事项
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 预警信息 */}
      {dashboardStats.overdue_count > 0 && (
        <Alert
          message="逾期预警"
          description={`当前有 ${dashboardStats.overdue_count} 个督办事项已逾期，请及时处理`}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
          action={
            <Button size="small" danger>
              查看详情
            </Button>
          }
        />
      )}

      {dashboardStats.urgent_count > 0 && (
        <Alert
          message="紧急事项"
          description={`当前有 ${dashboardStats.urgent_count} 个紧急督办事项需要关注`}
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
          action={
            <Button size="small">
              查看详情
            </Button>
          }
        />
      )}

      <Row gutter={[16, 16]}>
        {/* 逾期事项列表 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <span>
                <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
                逾期督办事项
              </span>
            }
            size="small"
            extra={<Button type="link">查看全部</Button>}
          >
            <Spin spinning={statsLoading}>
              <List
                dataSource={overdueItems?.data?.slice(0, 5) || []}
                renderItem={(item: SupervisionItem) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <span>
                          <Tag color={getStatusColor(item.status)}>
                            {item.status === 'overdue' ? '逾期' : '进行中'}
                          </Tag>
                          {item.title}
                        </span>
                      }
                      description={
                        <div>
                          <div style={{ marginBottom: 4 }}>
                            督办编号: {item.number}
                          </div>
                          <div style={{ color: '#ff4d4f' }}>
                            截止时间: {new Date(item.deadline).toLocaleDateString()}
                          </div>
                        </div>
                      }
                    />
                  </List.Item>
                )}
                locale={{ emptyText: '暂无逾期事项' }}
              />
            </Spin>
          </Card>
        </Col>

        {/* 紧急事项列表 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <span>
                <FireOutlined style={{ color: '#faad14', marginRight: 8 }} />
                紧急督办事项
              </span>
            }
            size="small"
            extra={<Button type="link">查看全部</Button>}
          >
            <Spin spinning={statsLoading}>
              <List
                dataSource={urgentItems?.data?.slice(0, 5) || []}
                renderItem={(item: SupervisionItem) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <span>
                          <Tag color={getUrgencyColor(item.urgency)}>
                            {item.urgency === 'high' ? '特急' : 
                             item.urgency === 'medium' ? '急办' : '一般'}
                          </Tag>
                          {item.title}
                        </span>
                      }
                      description={
                        <div>
                          <div style={{ marginBottom: 4 }}>
                            督办编号: {item.number}
                          </div>
                          <div>
                            截止时间: {new Date(item.deadline).toLocaleDateString()}
                          </div>
                          <Progress
                            percent={item.completion_rate}
                            size="small"
                            style={{ marginTop: 8 }}
                          />
                        </div>
                      }
                    />
                  </List.Item>
                )}
                locale={{ emptyText: '暂无紧急事项' }}
              />
            </Spin>
          </Card>
        </Col>
      </Row>

      {/* 数据更新时间 */}
      <div style={{ textAlign: 'center', marginTop: 24, color: '#666', fontSize: 12 }}>
        数据更新时间: {new Date().toLocaleString()}
      </div>
    </div>
  );
};

export default Dashboard;