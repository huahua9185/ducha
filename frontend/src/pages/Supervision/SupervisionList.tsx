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
  message,
  Progress,
  Tooltip,
  Popconfirm,
  Badge,
  Typography
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  FireOutlined,
  FileTextOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { supervisionService } from '@/services/supervisionService';
import { SupervisionItem, SupervisionStatus, UrgencyLevel, SupervisionType } from '@/types';
import './SupervisionList.css';

const { RangePicker } = DatePicker;
const { Text } = Typography;

interface SearchFilters {
  keyword?: string;
  status?: SupervisionStatus;
  urgency?: UrgencyLevel;
  type?: SupervisionType;
  dateRange?: [dayjs.Dayjs, dayjs.Dayjs];
  creator_id?: string;
  assignee_id?: string;
}

const SupervisionList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({});
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  // 获取督办事项列表
  const { data: supervisionData, isLoading, refetch } = useQuery(
    ['supervision-list', currentPage, pageSize, searchFilters],
    () => supervisionService.getSupervisionItems({
      page: currentPage,
      size: pageSize,
      ...searchFilters,
      start_date_from: searchFilters.dateRange?.[0]?.format('YYYY-MM-DD'),
      start_date_to: searchFilters.dateRange?.[1]?.format('YYYY-MM-DD')
    }),
    {
      keepPreviousData: true
    }
  );

  // 删除督办事项
  const deleteMutation = useMutation(
    (id: string) => supervisionService.deleteSupervisionItem(id),
    {
      onSuccess: () => {
        message.success('删除成功');
        queryClient.invalidateQueries('supervision-list');
        setSelectedRowKeys([]);
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '删除失败');
      }
    }
  );

  // 批量删除
  const batchDeleteMutation = useMutation(
    (ids: string[]) => Promise.all(ids.map(id => supervisionService.deleteSupervisionItem(id))),
    {
      onSuccess: () => {
        message.success('批量删除成功');
        queryClient.invalidateQueries('supervision-list');
        setSelectedRowKeys([]);
      },
      onError: (error: any) => {
        message.error('批量删除失败');
      }
    }
  );

  // 获取状态标签配置
  const getStatusConfig = (status: SupervisionStatus) => {
    const configs = {
      draft: { color: 'default', text: '草稿' },
      pending: { color: 'blue', text: '待办' },
      in_progress: { color: 'processing', text: '进行中' },
      completed: { color: 'success', text: '已完成' },
      overdue: { color: 'error', text: '逾期' },
      suspended: { color: 'warning', text: '暂停' },
      cancelled: { color: 'default', text: '已取消' }
    };
    return configs[status] || { color: 'default', text: status };
  };

  // 获取紧急程度标签配置
  const getUrgencyConfig = (urgency: UrgencyLevel) => {
    const configs = {
      low: { color: 'default', text: '一般', icon: null },
      medium: { color: 'warning', text: '急办', icon: <ClockCircleOutlined /> },
      high: { color: 'error', text: '特急', icon: <FireOutlined /> }
    };
    return configs[urgency] || { color: 'default', text: urgency, icon: null };
  };

  // 获取类型标签配置
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

  // 表格列定义
  const columns = [
    {
      title: '督办编号',
      dataIndex: 'number',
      key: 'number',
      width: 140,
      render: (text: string, record: SupervisionItem) => (
        <Button 
          type="link" 
          onClick={() => navigate(`/supervision/detail/${record.id}`)}
          style={{ padding: 0, fontSize: 13 }}
        >
          {text}
        </Button>
      )
    },
    {
      title: '督办事项',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text: string, record: SupervisionItem) => (
        <div>
          <div style={{ fontWeight: 500, marginBottom: 4 }}>
            {record.type === 'key' && <Badge color="gold" />}
            {text}
          </div>
          {record.description && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.description.substring(0, 50)}
              {record.description.length > 50 && '...'}
            </Text>
          )}
        </div>
      )
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: SupervisionType) => {
        const config = getTypeConfig(type);
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '紧急程度',
      dataIndex: 'urgency',
      key: 'urgency',
      width: 100,
      render: (urgency: UrgencyLevel) => {
        const config = getUrgencyConfig(urgency);
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: SupervisionStatus) => {
        const config = getStatusConfig(status);
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '进度',
      dataIndex: 'completion_rate',
      key: 'completion_rate',
      width: 120,
      render: (rate: number) => (
        <Progress
          percent={rate}
          size="small"
          strokeColor={rate >= 90 ? '#52c41a' : rate >= 60 ? '#1890ff' : '#faad14'}
        />
      )
    },
    {
      title: '责任人',
      dataIndex: 'assignee',
      key: 'assignee',
      width: 100,
      render: (assignee: any) => assignee?.real_name || assignee?.username || '-'
    },
    {
      title: '截止时间',
      dataIndex: 'deadline',
      key: 'deadline',
      width: 120,
      render: (deadline: string) => {
        const deadlineDate = dayjs(deadline);
        const now = dayjs();
        const isOverdue = deadlineDate.isBefore(now);
        
        return (
          <span style={{ color: isOverdue ? '#ff4d4f' : undefined }}>
            {deadlineDate.format('YYYY-MM-DD')}
            {isOverdue && <ExclamationCircleOutlined style={{ marginLeft: 4, color: '#ff4d4f' }} />}
          </span>
        );
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD')
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      fixed: 'right' as const,
      render: (_: any, record: SupervisionItem) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/supervision/detail/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => navigate(`/supervision/edit/${record.id}`)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个督办事项吗？"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
                loading={deleteMutation.isLoading}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  const data = supervisionData?.data?.items || [];
  const total = supervisionData?.data?.total || 0;

  // 行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedKeys: React.Key[]) => {
      setSelectedRowKeys(selectedKeys as string[]);
    },
    getCheckboxProps: (record: SupervisionItem) => ({
      disabled: record.status === 'completed',
    }),
  };

  return (
    <div className="supervision-list">
      <Card>
        {/* 搜索过滤器 */}
        <div className="search-filters" style={{ marginBottom: 16 }}>
          <Space wrap>
            <Input
              placeholder="搜索标题、编号"
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
              value={searchFilters.keyword}
              onChange={(e) => setSearchFilters(prev => ({ ...prev, keyword: e.target.value }))}
              onPressEnter={() => handleSearch(searchFilters)}
            />
            
            <Select
              placeholder="状态"
              style={{ width: 120 }}
              allowClear
              value={searchFilters.status}
              onChange={(value) => setSearchFilters(prev => ({ ...prev, status: value }))}
            >
              <Select.Option value="pending">待办</Select.Option>
              <Select.Option value="in_progress">进行中</Select.Option>
              <Select.Option value="completed">已完成</Select.Option>
              <Select.Option value="overdue">逾期</Select.Option>
              <Select.Option value="suspended">暂停</Select.Option>
            </Select>

            <Select
              placeholder="紧急程度"
              style={{ width: 120 }}
              allowClear
              value={searchFilters.urgency}
              onChange={(value) => setSearchFilters(prev => ({ ...prev, urgency: value }))}
            >
              <Select.Option value="low">一般</Select.Option>
              <Select.Option value="medium">急办</Select.Option>
              <Select.Option value="high">特急</Select.Option>
            </Select>

            <Select
              placeholder="类型"
              style={{ width: 120 }}
              allowClear
              value={searchFilters.type}
              onChange={(value) => setSearchFilters(prev => ({ ...prev, type: value }))}
            >
              <Select.Option value="regular">常规督办</Select.Option>
              <Select.Option value="key">重点督办</Select.Option>
              <Select.Option value="special">专项督办</Select.Option>
              <Select.Option value="emergency">应急督办</Select.Option>
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
              onClick={() => navigate('/supervision/create')}
            >
              新建督办
            </Button>
            
            {selectedRowKeys.length > 0 && (
              <Popconfirm
                title={`确定要删除选中的 ${selectedRowKeys.length} 个督办事项吗？`}
                onConfirm={() => {
                  const ids = selectedRowKeys.map(key => String(key));
                  batchDeleteMutation.mutate(ids);
                }}
                okText="确定"
                cancelText="取消"
              >
                <Button danger loading={batchDeleteMutation.isLoading}>
                  批量删除 ({selectedRowKeys.length})
                </Button>
              </Popconfirm>
            )}
          </Space>

          <div>
            共 {total} 条数据
          </div>
        </div>

        {/* 数据表格 */}
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={isLoading}
          rowSelection={rowSelection}
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
    </div>
  );
};

export default SupervisionList;