import React, { useState } from 'react';
import {
  Table,
  Card,
  Button,
  Tag,
  Space,
  Input,
  Select,
  DatePicker,
  Modal,
  Form,
  message,
  Progress,
  Tooltip,
  Typography,
  Avatar,
  Spin,
  Badge
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  UserOutlined,
  ReloadOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { 
  workflowService, 
  WorkflowInstance, 
  WorkflowStatus, 
  CreateWorkflowInstanceData 
} from '@/services/workflowService';
import './WorkflowInstances.css';

const { Search } = Input;
const { RangePicker } = DatePicker;
const { TextArea } = Input;
const { Text } = Typography;

interface SearchFilters {
  keyword?: string;
  status_filter?: WorkflowStatus;
  template_id?: string;
  business_type?: string;
  dateRange?: [dayjs.Dayjs, dayjs.Dayjs];
}

const WorkflowInstances: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({});
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  
  const [form] = Form.useForm();

  // 获取实例列表
  const { data: instancesData, isLoading, refetch } = useQuery(
    ['workflow-instances', currentPage, pageSize, searchFilters],
    () => workflowService.getInstanceList({
      page: currentPage,
      size: pageSize,
      ...searchFilters
    }),
    {
      keepPreviousData: true
    }
  );

  // 获取模板列表（用于创建实例）
  const { data: templatesData } = useQuery(
    'workflow-templates-all',
    () => workflowService.getTemplateList({ size: 1000, is_enabled: true })
  );

  // 启动实例
  const startMutation = useMutation(
    (id: string) => workflowService.startInstance(id),
    {
      onSuccess: () => {
        message.success('工作流启动成功');
        queryClient.invalidateQueries('workflow-instances');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '启动失败');
      }
    }
  );

  // 创建实例
  const createMutation = useMutation(
    (data: CreateWorkflowInstanceData) => workflowService.createInstance(data),
    {
      onSuccess: () => {
        message.success('工作流实例创建成功');
        setCreateModalVisible(false);
        form.resetFields();
        queryClient.invalidateQueries('workflow-instances');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '创建失败');
      }
    }
  );

  const data = instancesData?.data?.items || [];
  const total = instancesData?.data?.total || 0;
  const templates = templatesData?.data?.items || [];

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

  // 创建实例
  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      createMutation.mutate(values);
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 获取状态配置
  const getStatusConfig = (status: WorkflowStatus) => {
    const configs = {
      [WorkflowStatus.DRAFT]: { color: 'default', text: '草稿', icon: <ClockCircleOutlined /> },
      [WorkflowStatus.ACTIVE]: { color: 'processing', text: '运行中', icon: <PlayCircleOutlined /> },
      [WorkflowStatus.SUSPENDED]: { color: 'warning', text: '暂停', icon: <PauseCircleOutlined /> },
      [WorkflowStatus.COMPLETED]: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
      [WorkflowStatus.TERMINATED]: { color: 'error', text: '已终止', icon: <StopOutlined /> }
    };
    return configs[status] || { color: 'default', text: status, icon: null };
  };

  // 获取业务类型名称
  const getBusinessTypeName = (type: string) => {
    const names: Record<string, string> = {
      'supervision': '督办事项',
      'approval': '审批申请',
      'review': '审核事项',
      'notification': '通知事项'
    };
    return names[type] || type;
  };

  // 计算进度
  const calculateProgress = (instance: WorkflowInstance) => {
    if (instance.status === WorkflowStatus.COMPLETED) return 100;
    if (instance.status === WorkflowStatus.TERMINATED) return 0;
    // 这里应该根据实际的节点完成情况计算进度，暂时使用简单逻辑
    if (instance.status === WorkflowStatus.ACTIVE) return 50;
    if (instance.status === WorkflowStatus.SUSPENDED) return 30;
    return 0;
  };

  // 表格列定义
  const columns = [
    {
      title: '实例信息',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: WorkflowInstance) => (
        <div>
          <div style={{ fontWeight: 500, marginBottom: 4 }}>
            <Button 
              type="link" 
              onClick={() => navigate(`/workflow/instances/${record.id}`)}
              style={{ padding: 0, fontSize: 14 }}
            >
              {text}
            </Button>
          </div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            编号: {record.number}
          </Text>
        </div>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: WorkflowStatus) => {
        const config = getStatusConfig(status);
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 120,
      render: (_: any, record: WorkflowInstance) => {
        const progress = calculateProgress(record);
        return (
          <Progress
            percent={progress}
            size="small"
            strokeColor={progress === 100 ? '#52c41a' : progress >= 50 ? '#1890ff' : '#faad14'}
          />
        );
      }
    },
    {
      title: '业务类型',
      dataIndex: 'business_type',
      key: 'business_type',
      width: 100,
      render: (type: string) => type ? (
        <Tag color="blue">{getBusinessTypeName(type)}</Tag>
      ) : '-'
    },
    {
      title: '发起人',
      dataIndex: 'initiator',
      key: 'initiator',
      width: 100,
      render: (initiator: any) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <span>{initiator?.real_name || initiator?.username || '未知'}</span>
        </Space>
      )
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: number) => {
        const colors = ['default', 'blue', 'green', 'orange', 'red'];
        const texts = ['低', '较低', '普通', '较高', '高'];
        return (
          <Tag color={colors[priority - 1] || 'default'}>
            {texts[priority - 1] || '普通'}
          </Tag>
        );
      }
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 150,
      render: (time: string) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm')
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: WorkflowInstance) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/workflow/instances/${record.id}`)}
            />
          </Tooltip>
          
          {record.status === WorkflowStatus.DRAFT && (
            <Tooltip title="启动">
              <Button
                type="text"
                size="small"
                icon={<PlayCircleOutlined />}
                onClick={() => startMutation.mutate(record.id)}
                loading={startMutation.isLoading}
              />
            </Tooltip>
          )}
          
          {record.status === WorkflowStatus.ACTIVE && (
            <Tooltip title="暂停">
              <Button
                type="text"
                size="small"
                icon={<PauseCircleOutlined />}
                onClick={() => {
                  // TODO: 实现暂停功能
                  message.info('暂停功能开发中');
                }}
              />
            </Tooltip>
          )}
          
          {[WorkflowStatus.ACTIVE, WorkflowStatus.SUSPENDED].includes(record.status) && (
            <Tooltip title="终止">
              <Button
                type="text"
                size="small"
                danger
                icon={<StopOutlined />}
                onClick={() => {
                  // TODO: 实现终止功能
                  message.info('终止功能开发中');
                }}
              />
            </Tooltip>
          )}
        </Space>
      )
    }
  ];

  return (
    <div className="workflow-instances">
      <Card>
        {/* 搜索过滤器 */}
        <div className="search-filters" style={{ marginBottom: 16 }}>
          <Space wrap>
            <Search
              placeholder="搜索实例标题、编号"
              style={{ width: 250 }}
              value={searchFilters.keyword}
              onChange={(e) => setSearchFilters(prev => ({ ...prev, keyword: e.target.value }))}
              onSearch={() => handleSearch(searchFilters)}
              enterButton
            />
            
            <Select
              placeholder="状态"
              style={{ width: 120 }}
              allowClear
              value={searchFilters.status_filter}
              onChange={(value) => setSearchFilters(prev => ({ ...prev, status_filter: value }))}
            >
              <Select.Option value={WorkflowStatus.DRAFT}>草稿</Select.Option>
              <Select.Option value={WorkflowStatus.ACTIVE}>运行中</Select.Option>
              <Select.Option value={WorkflowStatus.SUSPENDED}>暂停</Select.Option>
              <Select.Option value={WorkflowStatus.COMPLETED}>已完成</Select.Option>
              <Select.Option value={WorkflowStatus.TERMINATED}>已终止</Select.Option>
            </Select>

            <Select
              placeholder="业务类型"
              style={{ width: 120 }}
              allowClear
              value={searchFilters.business_type}
              onChange={(value) => setSearchFilters(prev => ({ ...prev, business_type: value }))}
            >
              <Select.Option value="supervision">督办事项</Select.Option>
              <Select.Option value="approval">审批申请</Select.Option>
              <Select.Option value="review">审核事项</Select.Option>
              <Select.Option value="notification">通知事项</Select.Option>
            </Select>

            <RangePicker
              placeholder={['开始时间', '结束时间']}
              value={searchFilters.dateRange}
              onChange={(dates) => setSearchFilters(prev => ({ ...prev, dateRange: dates as [dayjs.Dayjs, dayjs.Dayjs] }))}
            />

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
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              创建实例
            </Button>
          </Space>

          <div>
            共 {total} 个实例
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
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 创建实例弹窗 */}
      <Modal
        title="创建工作流实例"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        onOk={handleCreate}
        confirmLoading={createMutation.isLoading}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            priority: 3
          }}
        >
          <Form.Item
            name="title"
            label="实例标题"
            rules={[
              { required: true, message: '请输入实例标题' },
              { max: 200, message: '标题不能超过200个字符' }
            ]}
          >
            <Input placeholder="请输入实例标题" />
          </Form.Item>

          <Form.Item
            name="template_id"
            label="工作流模板"
            rules={[{ required: true, message: '请选择工作流模板' }]}
          >
            <Select placeholder="请选择工作流模板" showSearch>
              {templates.map((template: any) => (
                <Select.Option key={template.id} value={template.id}>
                  <div>
                    <div>{template.name}</div>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {template.code} - {template.type}
                    </Text>
                  </div>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="business_type"
            label="业务类型"
          >
            <Select placeholder="请选择业务类型" allowClear>
              <Select.Option value="supervision">督办事项</Select.Option>
              <Select.Option value="approval">审批申请</Select.Option>
              <Select.Option value="review">审核事项</Select.Option>
              <Select.Option value="notification">通知事项</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="business_id"
            label="关联业务ID"
          >
            <Input placeholder="如果关联具体业务，请输入业务ID" />
          </Form.Item>

          <Form.Item
            name="priority"
            label="优先级"
            rules={[{ required: true, message: '请选择优先级' }]}
          >
            <Select>
              <Select.Option value={1}>低</Select.Option>
              <Select.Option value={2}>较低</Select.Option>
              <Select.Option value={3}>普通</Select.Option>
              <Select.Option value={4}>较高</Select.Option>
              <Select.Option value={5}>高</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WorkflowInstances;