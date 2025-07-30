import React, { useState } from 'react';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Progress,
  Timeline,
  Tabs,
  Table,
  Modal,
  Form,
  Input,
  Rate,
  message,
  Spin,
  Badge,
  Divider,
  Avatar,
  Typography,
  Upload,
  List,
  Tooltip
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FireOutlined,
  UserOutlined,
  CalendarOutlined,
  FileTextOutlined,
  PlusOutlined,
  UploadOutlined,
  DownloadOutlined,
  EyeOutlined,
  CommentOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import dayjs from 'dayjs';
import { supervisionService } from '@/services/supervisionService';
import { SupervisionItem, SupervisionStatus, UrgencyLevel, SupervisionType } from '@/types';
import './SupervisionDetail.css';

const { TextArea } = Input;
const { Text, Title } = Typography;
const { TabPane } = Tabs;

interface ProgressReportForm {
  title: string;
  content: string;
  progress_rate: number;
  completed_work?: string;
  next_plan?: string;
  issues?: string;
  support_needed?: string;
  estimated_completion?: string;
  risk_assessment?: string;
  is_important: boolean;
  task_assignment_id?: string;
}

const SupervisionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [reportModalVisible, setReportModalVisible] = useState(false);
  const [statusModalVisible, setStatusModalVisible] = useState(false);
  const [form] = Form.useForm<ProgressReportForm>();
  const [selectedStatus, setSelectedStatus] = useState<SupervisionStatus>(SupervisionStatus.PENDING);

  // 获取督办事项详情
  const { data: supervisionData, isLoading } = useQuery(
    ['supervision-detail', id],
    () => supervisionService.getSupervisionItem(id!),
    {
      enabled: !!id
    }
  );

  // 获取进度报告
  const { data: progressReports } = useQuery(
    ['supervision-progress', id],
    () => supervisionService.getProgressReports(id!),
    {
      enabled: !!id
    }
  );

  // 获取状态日志
  const { data: statusLogs } = useQuery(
    ['supervision-status-logs', id],
    () => supervisionService.getStatusLogs(id!),
    {
      enabled: !!id
    }
  );

  // 提交进度报告
  const submitReportMutation = useMutation(
    (data: ProgressReportForm) => supervisionService.createProgressReport(id!, data),
    {
      onSuccess: () => {
        message.success('进度报告提交成功');
        setReportModalVisible(false);
        form.resetFields();
        queryClient.invalidateQueries(['supervision-progress', id]);
        queryClient.invalidateQueries(['supervision-detail', id]);
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '提交失败');
      }
    }
  );

  // 更新状态
  const updateStatusMutation = useMutation(
    (status: SupervisionStatus) => supervisionService.changeSupervisionStatus(id!, status, '状态更新'),
    {
      onSuccess: () => {
        message.success('状态更新成功');
        setStatusModalVisible(false);
        queryClient.invalidateQueries(['supervision-detail', id]);
        queryClient.invalidateQueries(['supervision-status-logs', id]);
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '状态更新失败');
      }
    }
  );

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!supervisionData?.data) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Title level={4}>督办事项不存在</Title>
        <Button onClick={() => navigate('/supervision/list')}>返回列表</Button>
      </div>
    );
  }

  const supervision = supervisionData.data;
  const reports = Array.isArray(progressReports?.data) ? progressReports?.data : [];
  const logs = statusLogs?.data || [];

  // 获取状态配置
  const getStatusConfig = (status: SupervisionStatus) => {
    const configs = {
      draft: { color: 'default', text: '草稿', icon: <FileTextOutlined /> },
      pending: { color: 'blue', text: '待办', icon: <ClockCircleOutlined /> },
      in_progress: { color: 'processing', text: '进行中', icon: <PlayCircleOutlined /> },
      completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
      overdue: { color: 'error', text: '逾期', icon: <FireOutlined /> },
      suspended: { color: 'warning', text: '暂停', icon: <PauseCircleOutlined /> },
      cancelled: { color: 'default', text: '已取消', icon: <ClockCircleOutlined /> }
    };
    return configs[status] || { color: 'default', text: status, icon: null };
  };

  // 获取紧急程度配置
  const getUrgencyConfig = (urgency: UrgencyLevel) => {
    const configs = {
      low: { color: 'default', text: '一般', icon: null },
      medium: { color: 'warning', text: '急办', icon: <ClockCircleOutlined /> },
      high: { color: 'error', text: '特急', icon: <FireOutlined /> }
    };
    return configs[urgency] || { color: 'default', text: urgency, icon: null };
  };

  // 获取类型配置
  const getTypeConfig = (type: SupervisionType) => {
    const configs = {
      regular: { color: 'blue', text: '常规督办' },
      key: { color: 'gold', text: '重点督办' },
      special: { color: 'purple', text: '专项督办' },
      emergency: { color: 'red', text: '应急督办' },
      follow_up: { color: 'cyan', text: '跟进督办' }
    };
    return configs[type] || { color: 'default', text: type };
  };

  const statusConfig = getStatusConfig(supervision.status as SupervisionStatus);
  const urgencyConfig = getUrgencyConfig(supervision.urgency as UrgencyLevel);
  const typeConfig = getTypeConfig(supervision.type as SupervisionType);

  // 是否逾期
  const isOverdue = dayjs(supervision.deadline).isBefore(dayjs()) && supervision.status !== 'completed';

  // 进度报告表格列
  const reportColumns = [
    {
      title: '报告时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm')
    },
    {
      title: '进度',
      dataIndex: 'completion_rate',
      key: 'completion_rate',
      width: 120,
      render: (rate: number) => (
        <Progress percent={rate} size="small" />
      )
    },
    {
      title: '报告内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true
    },
    {
      title: '报告人',
      dataIndex: 'reporter',
      key: 'reporter',
      width: 100,
      render: (reporter: any) => reporter?.real_name || reporter?.username || '-'
    }
  ];

  return (
    <div className="supervision-detail">
      {/* 头部操作栏 */}
      <Card className="detail-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Button 
              type="text" 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/supervision/list')}
            >
              返回列表
            </Button>
            <Divider type="vertical" />
            <Title level={4} style={{ margin: 0 }}>
              {supervision.title}
            </Title>
            {supervision.type === 'key' && <Badge color="gold" text="重点督办" />}
            {isOverdue && <Badge color="red" text="已逾期" />}
          </Space>
          
          <Space>
            <Button
              icon={<CommentOutlined />}
              onClick={() => setReportModalVisible(true)}
              disabled={supervision.status === 'completed' || supervision.status === 'cancelled'}
            >
              汇报进度
            </Button>
            <Button
              icon={<EditOutlined />}
              onClick={() => navigate(`/supervision/edit/${id}`)}
            >
              编辑
            </Button>
            <Button
              type="primary"
              onClick={() => setStatusModalVisible(true)}
              disabled={supervision.status === 'completed' || supervision.status === 'cancelled'}
            >
              更新状态
            </Button>
          </Space>
        </div>
      </Card>

      <Tabs defaultActiveKey="basic" className="detail-tabs">
        {/* 基本信息 */}
        <TabPane tab="基本信息" key="basic">
          <Card>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="督办编号" span={1}>
                <Text copyable>{supervision.number}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="创建时间" span={1}>
                {dayjs(supervision.created_at).format('YYYY-MM-DD HH:mm')}
              </Descriptions.Item>
              
              <Descriptions.Item label="督办类型" span={1}>
                <Tag color={typeConfig.color}>{typeConfig.text}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="紧急程度" span={1}>
                <Tag color={urgencyConfig.color} icon={urgencyConfig.icon}>
                  {urgencyConfig.text}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="当前状态" span={1}>
                <Tag color={statusConfig.color} icon={statusConfig.icon}>
                  {statusConfig.text}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="完成进度" span={1}>
                <Progress percent={supervision.completion_rate} size="small" />
              </Descriptions.Item>
              
              <Descriptions.Item label="责任人" span={1}>
                <Space>
                  <Avatar size="small" icon={<UserOutlined />} />
                  {supervision.assignee?.real_name || supervision.assignee?.username || '-'}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="责任部门" span={1}>
                {supervision.responsible_department?.name || '-'}
              </Descriptions.Item>
              
              <Descriptions.Item label="督办部门" span={1}>
                {supervision.creator_department?.name || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="督办来源" span={1}>
                {supervision.source}
              </Descriptions.Item>
              
              <Descriptions.Item label="截止时间" span={1}>
                <Space>
                  <CalendarOutlined />
                  <span style={{ color: isOverdue ? '#ff4d4f' : undefined }}>
                    {dayjs(supervision.deadline).format('YYYY-MM-DD HH:mm')}
                  </span>
                  {isOverdue && <Tag color="red">已逾期</Tag>}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="预估工时" span={1}>
                {supervision.estimated_hours ? `${supervision.estimated_hours} 小时` : '-'}
              </Descriptions.Item>
              
              <Descriptions.Item label="详细描述" span={2}>
                <div style={{ whiteSpace: 'pre-wrap' }}>
                  {supervision.description || '暂无描述'}
                </div>
              </Descriptions.Item>
              
              {supervision.requirements && (
                <Descriptions.Item label="具体要求" span={2}>
                  <div style={{ whiteSpace: 'pre-wrap' }}>
                    {supervision.requirements}
                  </div>
                </Descriptions.Item>
              )}
              
              {supervision.expected_result && (
                <Descriptions.Item label="预期结果" span={2}>
                  <div style={{ whiteSpace: 'pre-wrap' }}>
                    {supervision.expected_result}
                  </div>
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>
        </TabPane>

        {/* 进度报告 */}
        <TabPane tab={`进度报告 (${reports?.length || 0})`} key="progress">
          <Card
            title="进度报告"
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setReportModalVisible(true)}
                disabled={supervision.status === 'completed' || supervision.status === 'cancelled'}
              >
                添加报告
              </Button>
            }
          >
            <Table
              columns={reportColumns}
              dataSource={reports}
              rowKey="id"
              pagination={false}
              expandable={{
                expandedRowRender: (record) => (
                  <div style={{ padding: '16px 0' }}>
                    <div style={{ marginBottom: 8 }}>
                      <Text strong>报告内容：</Text>
                    </div>
                    <div style={{ marginBottom: 16, whiteSpace: 'pre-wrap' }}>
                      {record?.content || '暂无内容'}
                    </div>
                    {record?.next_plan && (
                      <>
                        <div style={{ marginBottom: 8 }}>
                          <Text strong>下步计划：</Text>
                        </div>
                        <div style={{ whiteSpace: 'pre-wrap' }}>
                          {record?.next_plan}
                        </div>
                      </>
                    )}
                  </div>
                )
              }}
            />
          </Card>
        </TabPane>

        {/* 状态记录 */}
        <TabPane tab={`状态记录 (${logs.length})`} key="status">
          <Card title="状态变更记录">
            <Timeline>
              {logs.map((log: any) => (
                <Timeline.Item
                  key={log.id}
                  dot={getStatusConfig(log.new_status).icon}
                  color={getStatusConfig(log.new_status).color}
                >
                  <div>
                    <Space>
                      <Text strong>{getStatusConfig(log.new_status).text}</Text>
                      <Text type="secondary">
                        {dayjs(log.created_at).format('YYYY-MM-DD HH:mm')}
                      </Text>
                    </Space>
                  </div>
                  <div style={{ marginTop: 4 }}>
                    <Text type="secondary">
                      操作人：{log.operator?.real_name || log.operator?.username}
                    </Text>
                  </div>
                  {log.remark && (
                    <div style={{ marginTop: 4, color: '#666' }}>
                      备注：{log.remark}
                    </div>
                  )}
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </TabPane>
      </Tabs>

      {/* 进度报告弹窗 */}
      <Modal
        title="提交进度报告"
        open={reportModalVisible}
        onCancel={() => setReportModalVisible(false)}
        onOk={() => form.submit()}
        confirmLoading={submitReportMutation.isLoading}
      >
        <Form form={form} layout="vertical" onFinish={submitReportMutation.mutate}>
          <Form.Item
            name="progress_rate"
            label="完成进度"
            rules={[
              { required: true, message: '请设置完成进度' },
              { type: 'number', min: 0, max: 100, message: '进度必须在0-100之间' }
            ]}
          >
            <Progress
              percent={form.getFieldValue('progress_rate') || 0}
              format={(percent) => (
                <div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={percent || 0}
                    onChange={(e) => form.setFieldsValue({ progress_rate: parseInt(e.target.value) })}
                    style={{ width: '100%', margin: '8px 0' }}
                  />
                  <div style={{ textAlign: 'center' }}>{percent}%</div>
                </div>
              )}
            />
          </Form.Item>
          
          <Form.Item
            name="content"
            label="报告内容"
            rules={[
              { required: true, message: '请输入报告内容' },
              { max: 2000, message: '报告内容不能超过2000字符' }
            ]}
          >
            <TextArea
              rows={4}
              placeholder="请详细描述当前工作进展、遇到的问题和解决方案等"
            />
          </Form.Item>
          
          <Form.Item
            name="next_plan"
            label="下步计划"
            rules={[{ max: 1000, message: '下步计划不能超过1000字符' }]}
          >
            <TextArea
              rows={3}
              placeholder="请描述下一步的工作计划和安排"
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 状态更新弹窗 */}
      <Modal
        title="更新督办状态"
        open={statusModalVisible}
        onCancel={() => setStatusModalVisible(false)}
        onOk={() => updateStatusMutation.mutate(selectedStatus)}
        confirmLoading={updateStatusMutation.isLoading}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>当前状态：<Tag color={statusConfig.color}>{statusConfig.text}</Tag></div>
          <div>
            <Text>更新为：</Text>
            <Space wrap style={{ marginTop: 8 }}>
              {(['pending', 'in_progress', 'completed', 'suspended', 'cancelled'] as SupervisionStatus[]).map(status => {
                const config = getStatusConfig(status);
                return (
                  <Tag.CheckableTag
                    key={status}
                    checked={selectedStatus === status}
                    onChange={() => setSelectedStatus(status)}
                  >
                    {config.text}
                  </Tag.CheckableTag>
                );
              })}
            </Space>
          </div>
        </Space>
      </Modal>
    </div>
  );
};

export default SupervisionDetail;