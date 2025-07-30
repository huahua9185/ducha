import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Select,
  DatePicker,
  Space,
  Button,
  Table,
  Progress,
  Tag,
  Typography,
  Spin
} from 'antd';
import {
  BarChartOutlined,
  RiseOutlined,
  PieChartOutlined,
  LineChartOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import dayjs from 'dayjs';
import { analyticsService } from '@/services/analyticsService';
import './AnalyticsOverview.css';

const { RangePicker } = DatePicker;
const { Title, Text } = Typography;

interface AnalyticsData {
  summary: {
    total_items: number;
    completed_items: number;
    in_progress_items: number;
    overdue_items: number;
    completion_rate: number;
    average_completion_days: number;
    efficiency_score: number;
  };
  department_stats: Array<{
    department_id: number;
    department_name: string;
    total_items: number;
    completed_items: number;
    completion_rate: number;
    average_efficiency_score: number;
  }>;
  type_stats: Array<{
    type: string;
    count: number;
    completion_rate: number;
  }>;
  urgency_stats: Array<{
    urgency: string;
    count: number;
    completion_rate: number;
  }>;
  monthly_trend: Array<{
    month: string;
    created: number;
    completed: number;
    completion_rate: number;
  }>;
}

const AnalyticsOverview: React.FC = () => {
  const [timeRange, setTimeRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(3, 'month'),
    dayjs()
  ]);
  const [departmentId, setDepartmentId] = useState<number | undefined>();

  // 获取分析数据
  const { data: analyticsData, isLoading, refetch } = useQuery(
    ['analytics-overview', timeRange, departmentId],
    () => analyticsService.getAnalyticsOverview({
      start_date: timeRange[0].format('YYYY-MM-DD'),
      end_date: timeRange[1].format('YYYY-MM-DD'),
      department_id: departmentId
    }),
    {
      keepPreviousData: true
    }
  );

  const data: AnalyticsData = analyticsData?.data || {
    summary: {
      total_items: 0,
      completed_items: 0,
      in_progress_items: 0,
      overdue_items: 0,
      completion_rate: 0,
      average_completion_days: 0,
      efficiency_score: 0
    },
    department_stats: [],
    type_stats: [],
    urgency_stats: [],
    monthly_trend: []
  };

  // 部门统计表格列
  const departmentColumns = [
    {
      title: '部门名称',
      dataIndex: 'department_name',
      key: 'department_name'
    },
    {
      title: '督办总数',
      dataIndex: 'total_items',
      key: 'total_items',
      sorter: (a: any, b: any) => a.total_items - b.total_items
    },
    {
      title: '已完成',
      dataIndex: 'completed_items',
      key: 'completed_items',
      sorter: (a: any, b: any) => a.completed_items - b.completed_items
    },
    {
      title: '完成率',
      dataIndex: 'completion_rate',
      key: 'completion_rate',
      sorter: (a: any, b: any) => a.completion_rate - b.completion_rate,
      render: (rate: number) => (
        <Progress 
          percent={rate} 
          size="small" 
          strokeColor={rate >= 80 ? '#52c41a' : rate >= 60 ? '#1890ff' : '#faad14'}
        />
      )
    },
    {
      title: '效率评分',
      dataIndex: 'average_efficiency_score',
      key: 'average_efficiency_score',
      sorter: (a: any, b: any) => a.average_efficiency_score - b.average_efficiency_score,
      render: (score: number) => (
        <span style={{ 
          color: score >= 4 ? '#52c41a' : score >= 3 ? '#1890ff' : '#faad14',
          fontWeight: 'bold'
        }}>
          {score.toFixed(1)}分
        </span>
      )
    }
  ];

  // 类型统计表格列
  const typeColumns = [
    {
      title: '督办类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const typeNames: Record<string, string> = {
          regular: '常规督办',
          key: '重点督办',
          special: '专项督办',
          emergency: '应急督办'
        };
        const colors: Record<string, string> = {
          regular: 'blue',
          key: 'gold',
          special: 'purple',
          emergency: 'red'
        };
        return <Tag color={colors[type]}>{typeNames[type] || type}</Tag>;
      }
    },
    {
      title: '数量',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count
    },
    {
      title: '完成率',
      dataIndex: 'completion_rate',
      key: 'completion_rate',
      sorter: (a: any, b: any) => a.completion_rate - b.completion_rate,
      render: (rate: number) => (
        <Progress 
          percent={rate} 
          size="small" 
          format={(percent) => `${percent?.toFixed(1)}%`}
        />
      )
    }
  ];

  // 紧急程度统计表格列
  const urgencyColumns = [
    {
      title: '紧急程度',
      dataIndex: 'urgency',
      key: 'urgency',
      render: (urgency: string) => {
        const urgencyNames: Record<string, string> = {
          low: '一般',
          medium: '急办',
          high: '特急'
        };
        const colors: Record<string, string> = {
          low: 'default',
          medium: 'warning',
          high: 'error'
        };
        return <Tag color={colors[urgency]}>{urgencyNames[urgency] || urgency}</Tag>;
      }
    },
    {
      title: '数量',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count
    },
    {
      title: '完成率',
      dataIndex: 'completion_rate',
      key: 'completion_rate',
      sorter: (a: any, b: any) => a.completion_rate - b.completion_rate,
      render: (rate: number) => (
        <Progress 
          percent={rate} 
          size="small" 
          format={(percent) => `${percent?.toFixed(1)}%`}
        />
      )
    }
  ];

  return (
    <div className="analytics-overview">
      <div className="analytics-header">
        <Title level={3}>统计分析概览</Title>
        <Space>
          <RangePicker
            value={timeRange}
            onChange={(dates) => setTimeRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
            format="YYYY-MM-DD"
          />
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            刷新
          </Button>
          <Button icon={<DownloadOutlined />} type="primary">
            导出报告
          </Button>
        </Space>
      </div>

      <Spin spinning={isLoading}>
        {/* 关键指标 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="督办总数"
                value={data.summary.total_items}
                prefix={<FileTextOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="已完成"
                value={data.summary.completed_items}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="进行中"
                value={data.summary.in_progress_items}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="逾期项目"
                value={data.summary.overdue_items}
                prefix={<ExclamationCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 效率指标 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={8}>
            <Card title="整体完成率" size="small">
              <div style={{ textAlign: 'center' }}>
                <Progress
                  type="circle"
                  percent={data.summary.completion_rate}
                  size={120}
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#87d068',
                  }}
                  format={(percent) => `${percent?.toFixed(1)}%`}
                />
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card title="平均完成天数" size="small">
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <div style={{ fontSize: 36, fontWeight: 'bold', color: '#1890ff' }}>
                  {data.summary.average_completion_days.toFixed(1)}
                </div>
                <div style={{ color: '#666', marginTop: 8 }}>天</div>
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card title="效率评分" size="small">
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <div style={{ 
                  fontSize: 36, 
                  fontWeight: 'bold', 
                  color: data.summary.efficiency_score >= 4 ? '#52c41a' : 
                         data.summary.efficiency_score >= 3 ? '#1890ff' : '#faad14'
                }}>
                  {data.summary.efficiency_score.toFixed(1)}
                </div>
                <div style={{ color: '#666', marginTop: 8 }}>分 (满分5分)</div>
              </div>
            </Card>
          </Col>
        </Row>

        {/* 统计表格 */}
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="部门统计" size="small">
              <Table
                columns={departmentColumns}
                dataSource={data.department_stats}
                rowKey="department_id"
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={12}>
            <Card title="类型统计" size="small">
              <Table
                columns={typeColumns}
                dataSource={data.type_stats}
                rowKey="type"
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="紧急程度统计" size="small">
              <Table
                columns={urgencyColumns}
                dataSource={data.urgency_stats}
                rowKey="urgency"
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
        </Row>

        {/* 趋势分析 */}
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col span={24}>
            <Card title="月度趋势" size="small">
              <div style={{ padding: '20px 0', textAlign: 'center' }}>
                <Text type="secondary">
                  <BarChartOutlined style={{ marginRight: 8 }} />
                  趋势图表功能正在开发中，敬请期待...
                </Text>
                <div style={{ marginTop: 16 }}>
                  {data.monthly_trend.map((item, index) => (
                    <div key={index} style={{ 
                      display: 'inline-block', 
                      margin: '0 16px', 
                      textAlign: 'center',
                      padding: '8px 12px',
                      background: '#f8f9fa',
                      borderRadius: '6px'
                    }}>
                      <div style={{ fontSize: 12, color: '#666' }}>{item.month}</div>
                      <div style={{ fontSize: 16, fontWeight: 'bold', color: '#1890ff' }}>
                        {item.created}
                      </div>
                      <div style={{ fontSize: 12, color: '#52c41a' }}>
                        完成: {item.completed}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      </Spin>

      {/* 数据更新时间 */}
      <div style={{ textAlign: 'center', marginTop: 24, color: '#666', fontSize: 12 }}>
        数据统计时间: {timeRange[0].format('YYYY-MM-DD')} 至 {timeRange[1].format('YYYY-MM-DD')}
        <br />
        更新时间: {new Date().toLocaleString()}
      </div>
    </div>
  );
};

export default AnalyticsOverview;