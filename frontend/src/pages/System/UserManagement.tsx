import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Modal,
  Form,
  Select,
  Switch,
  message,
  Tag,
  Avatar,
  Tooltip,
  Popconfirm,
  Row,
  Col
} from 'antd';
import {
  UserOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { User, UserCreate, UserUpdate, PaginatedResponse } from '@/types';
import { userService } from '@/services/userService';
import './UserManagement.css';

const { Option } = Select;

const UserManagement: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState<string>();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  // 获取用户列表
  const { data: usersData, isLoading } = useQuery(
    ['users', pagination.current, pagination.pageSize, searchText, selectedDepartment],
    () => userService.getUsers({
      page: pagination.current,
      size: pagination.pageSize,
      search: searchText || undefined,
      department_id: selectedDepartment
    }),
    {
      keepPreviousData: true
    }
  );

  // 获取部门列表
  const { data: departmentsData } = useQuery(
    ['departments'],
    () => userService.getDepartments()
  );

  const users: User[] = usersData?.data?.items || [];
  const total = usersData?.data?.total || 0;
  const departments = departmentsData?.data || [];

  // 创建用户
  const createUserMutation = useMutation(userService.createUser, {
    onSuccess: () => {
      message.success('用户创建成功');
      setIsModalVisible(false);
      form.resetFields();
      queryClient.invalidateQueries(['users']);
    },
    onError: (error: any) => {
      message.error(`创建失败: ${error.response?.data?.message || error.message}`);
    }
  });

  // 更新用户
  const updateUserMutation = useMutation(
    ({ id, data }: { id: string; data: UserUpdate }) => userService.updateUser(id, data),
    {
      onSuccess: () => {
        message.success('用户更新成功');
        setIsModalVisible(false);
        setEditingUser(null);
        form.resetFields();
        queryClient.invalidateQueries(['users']);
      },
      onError: (error: any) => {
        message.error(`更新失败: ${error.response?.data?.message || error.message}`);
      }
    }
  );

  // 删除用户
  const deleteUserMutation = useMutation(userService.deleteUser, {
    onSuccess: () => {
      message.success('用户删除成功');
      queryClient.invalidateQueries(['users']);
    },
    onError: (error: any) => {
      message.error(`删除失败: ${error.response?.data?.message || error.message}`);
    }
  });

  const handleSearch = (value: string) => {
    setSearchText(value);
    setPagination({ ...pagination, current: 1 });
  };

  const handleDepartmentChange = (departmentId: string) => {
    setSelectedDepartment(departmentId === 'all' ? undefined : departmentId);
    setPagination({ ...pagination, current: 1 });
  };

  const handleCreate = () => {
    setEditingUser(null);
    setIsModalVisible(true);
    form.resetFields();
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setIsModalVisible(true);
    form.setFieldsValue({
      ...user,
      password: '' // 不显示密码
    });
  };

  const handleDelete = (userId: string) => {
    deleteUserMutation.mutate(userId);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingUser) {
        // 更新用户
        const updateData: UserUpdate = { ...values };
        if (!values.password) {
          delete updateData.password;
        }
        updateUserMutation.mutate({ id: editingUser.id, data: updateData });
      } else {
        // 创建用户
        const createData: UserCreate = values;
        createUserMutation.mutate(createData);
      }
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    setEditingUser(null);
    form.resetFields();
  };

  const handleTableChange = (paginationConfig: any) => {
    setPagination({
      current: paginationConfig.current,
      pageSize: paginationConfig.pageSize
    });
  };

  const columns = [
    {
      title: '头像',
      dataIndex: 'avatar_url',
      key: 'avatar',
      width: 80,
      render: (avatar: string, record: User) => (
        <Avatar
          size={40}
          src={avatar}
          icon={<UserOutlined />}
          style={{ backgroundColor: '#1890ff' }}
        >
          {!avatar && record.real_name?.charAt(0)}
        </Avatar>
      )
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 120
    },
    {
      title: '真实姓名',
      dataIndex: 'real_name',
      key: 'real_name',
      width: 120
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200,
      ellipsis: true
    },
    {
      title: '手机号',
      dataIndex: 'phone',
      key: 'phone',
      width: 120
    },
    {
      title: '职位',
      dataIndex: 'position',
      key: 'position',
      width: 120,
      ellipsis: true
    },
    {
      title: '部门',
      dataIndex: 'department_name',
      key: 'department',
      width: 120,
      ellipsis: true
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '管理员',
      dataIndex: 'is_superuser',
      key: 'is_superuser',
      width: 80,
      render: (isSuperuser: boolean) => (
        <Tag color={isSuperuser ? 'red' : 'default'}>
          {isSuperuser ? '是' : '否'}
        </Tag>
      )
    },
    {
      title: '最后登录',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      width: 160,
      render: (time: string) => time ? new Date(time).toLocaleString() : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right' as const,
      render: (_: any, record: User) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => {
                // TODO: 实现查看用户详情
                message.info('查看用户详情功能开发中');
              }}
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
          <Tooltip title="删除">
            <Popconfirm
              title="确定要删除这个用户吗？"
              description="删除后无法恢复，请谨慎操作"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <div className="user-management">
      <Card>
        <Row gutter={[16, 16]} className="search-bar">
          <Col xs={24} sm={12} md={8} lg={6}>
            <Input.Search
              placeholder="搜索用户名、姓名或邮箱"
              allowClear
              onSearch={handleSearch}
              onChange={(e) => !e.target.value && handleSearch('')}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Select
              placeholder="选择部门"
              allowClear
              style={{ width: '100%' }}
              onChange={handleDepartmentChange}
            >
              <Option value="all">全部部门</Option>
              {departments.map((dept: any) => (
                <Option key={dept.id} value={dept.id}>
                  {dept.name}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={24} md={8} lg={12}>
            <Space className="action-buttons">
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreate}
              >
                新建用户
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => queryClient.invalidateQueries(['users'])}
              >
                刷新
              </Button>
            </Space>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            pageSizeOptions: ['10', '20', '50', '100']
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 创建/编辑用户弹窗 */}
      <Modal
        title={editingUser ? '编辑用户' : '新建用户'}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        confirmLoading={createUserMutation.isLoading || updateUserMutation.isLoading}
        width={600}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            is_active: true,
            is_superuser: false
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="username"
                label="用户名"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input placeholder="请输入用户名" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="real_name"
                label="真实姓名"
                rules={[{ required: true, message: '请输入真实姓名' }]}
              >
                <Input placeholder="请输入真实姓名" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="email"
                label="邮箱"
                rules={[
                  { type: 'email', message: '请输入有效的邮箱地址' },
                  { required: true, message: '请输入邮箱' }
                ]}
              >
                <Input placeholder="请输入邮箱" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="phone"
                label="手机号"
                rules={[
                  { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
                ]}
              >
                <Input placeholder="请输入手机号" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="employee_id"
                label="员工编号"
              >
                <Input placeholder="请输入员工编号" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="position"
                label="职位"
              >
                <Input placeholder="请输入职位" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="department_id"
                label="所属部门"
              >
                <Select placeholder="选择部门" allowClear>
                  {departments.map((dept: any) => (
                    <Option key={dept.id} value={dept.id}>
                      {dept.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="password"
                label={editingUser ? '新密码（留空则不修改）' : '密码'}
                rules={editingUser ? [] : [{ required: true, message: '请输入密码' }]}
              >
                <Input.Password placeholder={editingUser ? '留空则不修改密码' : '请输入密码'} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="is_active"
                label="启用状态"
                valuePropName="checked"
              >
                <Switch checkedChildren="启用" unCheckedChildren="禁用" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="is_superuser"
                label="管理员权限"
                valuePropName="checked"
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="bio"
            label="个人简介"
          >
            <Input.TextArea rows={3} placeholder="请输入个人简介" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;