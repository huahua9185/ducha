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
  Popconfirm,
  Switch,
  Tooltip,
  Badge,
  Typography,
  Spin
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CopyOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SettingOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { workflowService, WorkflowTemplate, CreateWorkflowTemplateData } from '@/services/workflowService';
import './WorkflowTemplates.css';

const { Search } = Input;
const { TextArea } = Input;
const { Text } = Typography;

interface SearchFilters {
  keyword?: string;
  type_filter?: string;
  is_enabled?: boolean;
}

const WorkflowTemplates: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({});
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<WorkflowTemplate | null>(null);
  
  const [form] = Form.useForm();

  // 获取模板列表
  const { data: templatesData, isLoading, refetch } = useQuery(
    ['workflow-templates', currentPage, pageSize, searchFilters],
    () => workflowService.getTemplateList({
      page: currentPage,
      size: pageSize,
      ...searchFilters
    }),
    {
      keepPreviousData: true
    }
  );

  // 删除模板
  const deleteMutation = useMutation(
    (id: string) => workflowService.deleteTemplate(id),
    {
      onSuccess: () => {
        message.success('删除成功');
        queryClient.invalidateQueries('workflow-templates');
        setSelectedRowKeys([]);
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '删除失败');
      }
    }
  );

  // 创建/更新模板
  const saveMutation = useMutation(
    (data: CreateWorkflowTemplateData) => {
      if (editingTemplate) {
        return workflowService.updateTemplate(editingTemplate.id, data);
      } else {
        return workflowService.createTemplate(data);
      }
    },
    {
      onSuccess: () => {
        message.success(editingTemplate ? '更新成功' : '创建成功');
        setModalVisible(false);
        setEditingTemplate(null);
        form.resetFields();
        queryClient.invalidateQueries('workflow-templates');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '操作失败');
      }
    }
  );

  const data = templatesData?.data?.items || [];
  const total = templatesData?.data?.total || 0;

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

  // 打开编辑弹窗
  const handleEdit = (template: WorkflowTemplate) => {
    setEditingTemplate(template);
    form.setFieldsValue({
      name: template.name,
      code: template.code,
      description: template.description,
      type: template.type,
      version: template.version,
      is_enabled: template.is_enabled,
      sort_order: template.sort_order
    });
    setModalVisible(true);
  };

  // 打开新建弹窗
  const handleCreate = () => {
    setEditingTemplate(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const templateData: CreateWorkflowTemplateData = {
        ...values,
        definition: {
          nodes: [],
          transitions: []
        }
      };
      saveMutation.mutate(templateData);
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 获取模板类型标签颜色
  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'supervision': 'blue',
      'approval': 'green',
      'review': 'orange',
      'notification': 'purple',
      'custom': 'default'
    };
    return colors[type] || 'default';
  };

  // 获取模板类型名称
  const getTypeName = (type: string) => {
    const names: Record<string, string> = {
      'supervision': '督办流程',
      'approval': '审批流程',
      'review': '审核流程',
      'notification': '通知流程',
      'custom': '自定义'
    };
    return names[type] || type;
  };

  // 表格列定义
  const columns = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: WorkflowTemplate) => (
        <div>
          <div style={{ fontWeight: 500, marginBottom: 4 }}>
            {record.is_builtin && <Badge color="gold" style={{ marginRight: 8 }} />}
            {text}
          </div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            编码: {record.code}
          </Text>
        </div>
      )
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type: string) => (
        <Tag color={getTypeColor(type)}>{getTypeName(type)}</Tag>
      )
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 80,
      render: (version: string) => (
        <Text code>{version}</Text>
      )
    },
    {
      title: '状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      render: (enabled: boolean) => (
        <Tag color={enabled ? 'success' : 'default'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      )
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
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: WorkflowTemplate) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/workflow/templates/${record.id}`)}
            />
          </Tooltip>
          
          <Tooltip title="编辑">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          
          <Tooltip title="设计流程">
            <Button
              type="text"
              size="small"
              icon={<SettingOutlined />}
              onClick={() => navigate(`/workflow/templates/${record.id}/design`)}
            />
          </Tooltip>
          
          <Tooltip title="复制">
            <Button
              type="text"
              size="small"
              icon={<CopyOutlined />}
              onClick={() => {
                // TODO: 实现复制功能
                message.info('复制功能开发中');
              }}
            />
          </Tooltip>
          
          {!record.is_builtin && (
            <Popconfirm
              title="确定要删除这个模板吗？"
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
          )}
        </Space>
      )
    }
  ];

  // 行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedKeys: React.Key[]) => {
      setSelectedRowKeys(selectedKeys as string[]);
    },
    getCheckboxProps: (record: WorkflowTemplate) => ({
      disabled: record.is_builtin,
    }),
  };

  return (
    <div className="workflow-templates">
      <Card>
        {/* 搜索过滤器 */}
        <div className="search-filters" style={{ marginBottom: 16 }}>
          <Space wrap>
            <Search
              placeholder="搜索模板名称、编码"
              style={{ width: 250 }}
              value={searchFilters.keyword}
              onChange={(e) => setSearchFilters(prev => ({ ...prev, keyword: e.target.value }))}
              onSearch={() => handleSearch(searchFilters)}
              enterButton
            />
            
            <Select
              placeholder="模板类型"
              style={{ width: 150 }}
              allowClear
              value={searchFilters.type_filter}
              onChange={(value) => setSearchFilters(prev => ({ ...prev, type_filter: value }))}
            >
              <Select.Option value="supervision">督办流程</Select.Option>
              <Select.Option value="approval">审批流程</Select.Option>
              <Select.Option value="review">审核流程</Select.Option>
              <Select.Option value="notification">通知流程</Select.Option>
              <Select.Option value="custom">自定义</Select.Option>
            </Select>

            <Select
              placeholder="状态"
              style={{ width: 120 }}
              allowClear
              value={searchFilters.is_enabled}
              onChange={(value) => setSearchFilters(prev => ({ ...prev, is_enabled: value }))}
            >
              <Select.Option value={true}>启用</Select.Option>
              <Select.Option value={false}>禁用</Select.Option>
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
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              新建模板
            </Button>
            
            {selectedRowKeys.length > 0 && (
              <Popconfirm
                title={`确定要删除选中的 ${selectedRowKeys.length} 个模板吗？`}
                onConfirm={() => {
                  selectedRowKeys.forEach(id => deleteMutation.mutate(id));
                }}
                okText="确定"
                cancelText="取消"
              >
                <Button danger loading={deleteMutation.isLoading}>
                  批量删除 ({selectedRowKeys.length})
                </Button>
              </Popconfirm>
            )}
          </Space>

          <div>
            共 {total} 个模板
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
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* 新建/编辑模板弹窗 */}
      <Modal
        title={editingTemplate ? '编辑工作流模板' : '新建工作流模板'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingTemplate(null);
          form.resetFields();
        }}
        onOk={handleSubmit}
        confirmLoading={saveMutation.isLoading}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            is_enabled: true,
            sort_order: 0,
            version: '1.0'
          }}
        >
          <Form.Item
            name="name"
            label="模板名称"
            rules={[
              { required: true, message: '请输入模板名称' },
              { max: 100, message: '名称不能超过100个字符' }
            ]}
          >
            <Input placeholder="请输入模板名称" />
          </Form.Item>

          <Form.Item
            name="code"
            label="模板编码"
            rules={[
              { required: true, message: '请输入模板编码' },
              { max: 50, message: '编码不能超过50个字符' },
              { pattern: /^[a-zA-Z0-9_-]+$/, message: '编码只能包含字母、数字、下划线和短横线' }
            ]}
          >
            <Input 
              placeholder="请输入模板编码" 
              disabled={!!editingTemplate}
            />
          </Form.Item>

          <Form.Item
            name="type"
            label="模板类型"
            rules={[{ required: true, message: '请选择模板类型' }]}
          >
            <Select placeholder="请选择模板类型">
              <Select.Option value="supervision">督办流程</Select.Option>
              <Select.Option value="approval">审批流程</Select.Option>
              <Select.Option value="review">审核流程</Select.Option>
              <Select.Option value="notification">通知流程</Select.Option>
              <Select.Option value="custom">自定义</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="version"
            label="版本号"
            rules={[{ required: true, message: '请输入版本号' }]}
          >
            <Input placeholder="如: 1.0" />
          </Form.Item>

          <Form.Item
            name="description"
            label="模板描述"
            rules={[{ max: 500, message: '描述不能超过500个字符' }]}
          >
            <TextArea 
              rows={3} 
              placeholder="请输入模板描述"
            />
          </Form.Item>

          <Form.Item
            name="sort_order"
            label="排序"
          >
            <Input type="number" placeholder="数字越小排序越靠前" />
          </Form.Item>

          <Form.Item
            name="is_enabled"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WorkflowTemplates;