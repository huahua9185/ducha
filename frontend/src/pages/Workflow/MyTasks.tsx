import React, { useState } from 'react';
import {
  Table,
  Card,
  Button,
  Tag,
  Space,
  Input,
  Select,
  Modal,
  Form,
  message,
  Tooltip,
  Typography,
  Avatar,
  Badge,
  Descriptions,
  Timeline,
  Spin,
  Rate,
  Progress
} from 'antd';
import {
  SearchOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlayCircleOutlined,
  UserOutlined,
  ReloadOutlined,
  CommentOutlined,
  FileTextOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { workflowService, WorkflowNode, NodeStatus, TaskCompleteData } from '@/services/workflowService';
import './MyTasks.css';

const { Search } = Input;
const { TextArea } = Input;
const { Text, Title } = Typography;

interface SearchFilters {
  keyword?: string;
  status_filter?: NodeStatus;
}

const MyTasks: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({});
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [completeModalVisible, setCompleteModalVisible] = useState(false);
  const [selectedTask, setSelectedTask] = useState<WorkflowNode | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  
  const [form] = Form.useForm();

  // 获取我的任务列表
  const { data: tasksData, isLoading, refetch } = useQuery(
    ['my-tasks', currentPage, pageSize, searchFilters],
    () => workflowService.getMyTasks({
      page: currentPage,
      size: pageSize,
      ...searchFilters
    }),
    {
      keepPreviousData: true,
      refetchInterval: 30000 // 每30秒刷新一次
    }
  );

  // 获取用户任务统计
  const { data: statsData } = useQuery(
    'user-task-stats',
    () => workflowService.getUserTaskStats(),
    {
      refetchInterval: 60000 // 每分钟刷新一次
    }
  );

  // 完成任务
  const completeMutation = useMutation(
    ({ taskId, data }: { taskId: string; data: TaskCompleteData }) => 
      workflowService.completeTask(taskId, data),
    {
      onSuccess: () => {
        message.success('任务完成成功');
        setCompleteModalVisible(false);
        setSelectedTask(null);
        form.resetFields();
        queryClient.invalidateQueries('my-tasks');
        queryClient.invalidateQueries('user-task-stats');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '完成任务失败');
      }
    }
  );

  const data = tasksData?.data?.items || [];
  const total = tasksData?.data?.total || 0;
  const stats = statsData?.data || {
    pending_tasks: 0,
    processing_tasks: 0,
    completed_tasks: 0,
    overdue_tasks: 0
  };

  // 处理搜索
  const handleSearch = (values: SearchFilters) => {
    setSearchFilters(values);
    setCurrentPage(1);
  };

  // 重置搜索
  const handleReset = () => {
    setSearchFilters({});
    setCurrentPage(1);
  };

  // 打开完成任务弹窗
  const handleCompleteTask = (task: WorkflowNode) => {
    setSelectedTask(task);
    setCompleteModalVisible(true);
  };

  // 提交完成任务
  const handleSubmitComplete = async () => {
    if (!selectedTask) return;
    
    try {
      const values = await form.validateFields();
      completeMutation.mutate({
        taskId: selectedTask.id,
        data: values
      });
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 查看任务详情
  const handleViewDetail = (task: WorkflowNode) => {
    setSelectedTask(task);
    setDetailModalVisible(true);
  };

  // 获取状态配置
  const getStatusConfig = (status: NodeStatus) => {
    const configs = {
      [NodeStatus.PENDING]: { color: 'default', text: '待处理', icon: <ClockCircleOutlined /> },
      [NodeStatus.ACTIVE]: { color: 'processing', text: '处理中', icon: <PlayCircleOutlined /> },
      [NodeStatus.COMPLETED]: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
      [NodeStatus.SKIPPED]: { color: 'warning', text: '已跳过', icon: <ExclamationCircleOutlined /> },
      [NodeStatus.FAILED]: { color: 'error', text: '失败', icon: <ExclamationCircleOutlined /> }
    };
    return configs[status] || { color: 'default', text: status, icon: null };
  };

  // 检查任务是否逾期
  const isOverdue = (task: WorkflowNode) => {
    if (!task.deadline) return false;
    return dayjs(task.deadline).isBefore(dayjs()) && task.status !== NodeStatus.COMPLETED;
  };

  // 计算剩余时间
  const getTimeRemaining = (task: WorkflowNode) => {
    if (!task.deadline) return null;
    const deadline = dayjs(task.deadline);
    const now = dayjs();
    
    if (deadline.isBefore(now)) {
      return { text: '已逾期', color: '#ff4d4f', overdue: true };
    }
    
    const hours = deadline.diff(now, 'hour');
    if (hours < 24) {
      return { text: `${hours}小时后到期`, color: '#faad14', overdue: false };
    }
    
    const days = deadline.diff(now, 'day');
    return { text: `${days}天后到期`, color: '#52c41a', overdue: false };
  };

  // 表格列定义
  const columns = [
    {
      title: '任务信息',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: WorkflowNode) => (
        <div>
          <div style={{ fontWeight: 500, marginBottom: 4 }}>
            {isOverdue(record) && <Badge color="red" style={{ marginRight: 8 }} />}
            <Button 
              type="link" 
              onClick={() => handleViewDetail(record)}
              style={{ padding: 0, fontSize: 14 }}
            >
              {text}
            </Button>
          </div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            工作流: {(record as any).workflow_instance?.title || '未知'}
          </Text>
        </div>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: NodeStatus) => {
        const config = getStatusConfig(status);
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: '截止时间',
      dataIndex: 'deadline',
      key: 'deadline',
      width: 150,
      render: (deadline: string, record: WorkflowNode) => {
        if (!deadline) return '-';
        
        const timeRemaining = getTimeRemaining(record);
        return (
          <div>
            <div>{dayjs(deadline).format('YYYY-MM-DD HH:mm')}</div>
            {timeRemaining && (
              <Text style={{ color: timeRemaining.color, fontSize: 12 }}>
                {timeRemaining.text}
              </Text>
            )}
          </div>
        );
      }
    },
    {
      title: '接收时间',
      dataIndex: 'enter_time',
      key: 'enter_time',
      width: 150,
      render: (time: string) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '处理时长',
      key: 'duration',
      width: 100,
      render: (_: any, record: WorkflowNode) => {
        if (!record.enter_time) return '-';
        
        const start = dayjs(record.enter_time);
        const end = record.complete_time ? dayjs(record.complete_time) : dayjs();
        const duration = end.diff(start, 'hour');
        
        if (duration < 1) {
          return `${end.diff(start, 'minute')}分钟`;
        } else if (duration < 24) {
          return `${duration}小时`;
        } else {
          return `${Math.floor(duration / 24)}天`;
        }
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: WorkflowNode) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          
          {[NodeStatus.PENDING, NodeStatus.ACTIVE].includes(record.status) && (
            <Tooltip title="完成任务">
              <Button
                type="text"
                size="small"
                icon={<CheckCircleOutlined />}
                onClick={() => handleCompleteTask(record)}
              />
            </Tooltip>
          )}
          
          <Tooltip title="查看工作流">
            <Button
              type="text"
              size="small"
              icon={<FileTextOutlined />}
              onClick={() => navigate(`/workflow/instances/${record.workflow_instance_id}`)}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <div className="my-tasks">
      {/* 统计卡片 */}
      <div className="task-stats" style={{ marginBottom: 24 }}>
        <Space size={16}>
          <Card size="small">
            <div className="stat-item">
              <div className="stat-number" style={{ color: '#1890ff' }}>
                {stats.pending_tasks}
              </div>
              <div className="stat-label">待处理</div>
            </div>
          </Card>
          
          <Card size="small">
            <div className="stat-item">
              <div className="stat-number" style={{ color: '#52c41a' }}>
                {stats.processing_tasks}
              </div>
              <div className="stat-label">处理中</div>
            </div>
          </Card>
          
          <Card size="small">
            <div className="stat-item">
              <div className="stat-number" style={{ color: '#722ed1' }}>
                {stats.completed_tasks}
              </div>
              <div className="stat-label">已完成</div>
            </div>
          </Card>
          
          <Card size="small">
            <div className="stat-item">
              <div className="stat-number" style={{ color: '#ff4d4f' }}>
                {stats.overdue_tasks}
              </div>
              <div className="stat-label">已逾期</div>
            </div>
          </Card>
        </Space>
      </div>

      <Card>
        {/* 搜索过滤器 */}
        <div className="search-filters" style={{ marginBottom: 16 }}>
          <Space wrap>
            <Search
              placeholder="搜索任务名称"
              style={{ width: 250 }}
              value={searchFilters.keyword}
              onChange={(e) => setSearchFilters(prev => ({ ...prev, keyword: e.target.value }))}
              onSearch={() => handleSearch(searchFilters)}
              enterButton
            />
            
            <Select
              placeholder="任务状态"
              style={{ width: 120 }}
              allowClear
              value={searchFilters.status_filter}
              onChange={(value) => setSearchFilters(prev => ({ ...prev, status_filter: value }))}
            >
              <Select.Option value={NodeStatus.PENDING}>待处理</Select.Option>
              <Select.Option value={NodeStatus.ACTIVE}>处理中</Select.Option>
              <Select.Option value={NodeStatus.COMPLETED}>已完成</Select.Option>
            </Select>

            <Button type="primary" onClick={() => handleSearch(searchFilters)}>
              搜索
            </Button>
            <Button onClick={handleReset}>重置</Button>
            <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
              刷新
            </Button>
          </Space>
        </div>

        {/* 操作栏 */}
        <div className="action-bar" style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <div>
            <Text strong>我的待办任务</Text>
          </div>
          <div>
            共 {total} 个任务
          </div>
        </div>

        {/* 数据表格 */}
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: currentPage,
            pageSize,
            total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size || 10);
            }
          }}
          scroll={{ x: 1000 }}
          rowClassName={(record: WorkflowNode) => {
            if (isOverdue(record)) return 'overdue-row';
            if (record.status === NodeStatus.PENDING) return 'pending-row';
            return '';
          }}
        />
      </Card>

      {/* 完成任务弹窗 */}
      <Modal
        title="完成任务"
        open={completeModalVisible}
        onCancel={() => {
          setCompleteModalVisible(false);
          setSelectedTask(null);
          form.resetFields();
        }}
        onOk={handleSubmitComplete}
        confirmLoading={completeMutation.isLoading}
        width={600}
      >
        {selectedTask && (
          <div>
            <Descriptions column={1} size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="任务名称">{selectedTask.name}</Descriptions.Item>
              <Descriptions.Item label="工作流实例">
                {(selectedTask as any).workflow_instance?.title}
              </Descriptions.Item>
              <Descriptions.Item label="截止时间">
                {selectedTask.deadline ? dayjs(selectedTask.deadline).format('YYYY-MM-DD HH:mm') : '无'}
              </Descriptions.Item>
            </Descriptions>
            
            <Form form={form} layout="vertical">
              <Form.Item
                name="result"
                label="处理结果"
                rules={[{ required: true, message: '请选择处理结果' }]}
              >
                <Select placeholder="请选择处理结果">
                  <Select.Option value="approved">通过</Select.Option>
                  <Select.Option value="rejected">拒绝</Select.Option>
                  <Select.Option value="completed">完成</Select.Option>
                </Select>
              </Form.Item>
              
              <Form.Item
                name="comment"
                label="处理意见"
                rules={[
                  { required: true, message: '请输入处理意见' },
                  { max: 1000, message: '处理意见不能超过1000个字符' }
                ]}
              >
                <TextArea
                  rows={4}
                  placeholder="请输入处理意见"
                />
              </Form.Item>
            </Form>
          </div>
        )}
      </Modal>

      {/* 任务详情弹窗 */}
      <Modal
        title="任务详情"
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedTask(null);
        }}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          selectedTask && [NodeStatus.PENDING, NodeStatus.ACTIVE].includes(selectedTask.status) && (
            <Button
              key="complete"
              type="primary"
              onClick={() => {
                setDetailModalVisible(false);
                handleCompleteTask(selectedTask);
              }}
            >
              完成任务
            </Button>
          )
        ]}
        width={800}
      >
        {selectedTask && (
          <div>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="任务名称" span={2}>
                {selectedTask.name}
              </Descriptions.Item>
              <Descriptions.Item label="任务状态">
                <Tag color={getStatusConfig(selectedTask.status).color}>
                  {getStatusConfig(selectedTask.status).text}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="工作流实例">
                {(selectedTask as any).workflow_instance?.title || '未知'}
              </Descriptions.Item>
              <Descriptions.Item label="接收时间">
                {selectedTask.enter_time ? dayjs(selectedTask.enter_time).format('YYYY-MM-DD HH:mm') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="截止时间">
                {selectedTask.deadline ? dayjs(selectedTask.deadline).format('YYYY-MM-DD HH:mm') : '无'}
              </Descriptions.Item>
              <Descriptions.Item label="开始处理时间">
                {selectedTask.start_time ? dayjs(selectedTask.start_time).format('YYYY-MM-DD HH:mm') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="完成时间">
                {selectedTask.complete_time ? dayjs(selectedTask.complete_time).format('YYYY-MM-DD HH:mm') : '-'}
              </Descriptions.Item>
              {selectedTask.comment && (
                <Descriptions.Item label="处理意见" span={2}>
                  <div style={{ whiteSpace: 'pre-wrap' }}>
                    {selectedTask.comment}
                  </div>
                </Descriptions.Item>
              )}
            </Descriptions>
            
            {selectedTask.node_data && (
              <div style={{ marginTop: 16 }}>
                <Title level={5}>节点配置</Title>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                  {JSON.stringify(selectedTask.node_data, null, 2)}
                </pre>
              </div>
            )}
            
            {selectedTask.form_data && (
              <div style={{ marginTop: 16 }}>
                <Title level={5}>表单数据</Title>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                  {JSON.stringify(selectedTask.form_data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default MyTasks;