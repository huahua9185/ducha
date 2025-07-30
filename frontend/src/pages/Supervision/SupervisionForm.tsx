import React, { useEffect, useState } from 'react';
import {
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Card,
  Row,
  Col,
  message,
  Spin,
  Space,
  Upload,
  Tag,
  Divider,
  Switch,
  InputNumber
} from 'antd';
import {
  SaveOutlined,
  ArrowLeftOutlined,
  UploadOutlined,
  UserOutlined,
  CalendarOutlined,
  FileTextOutlined,
  BankOutlined
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import dayjs from 'dayjs';
import { supervisionService } from '@/services/supervisionService';
import { userService } from '@/services/userService';
import { departmentService } from '@/services/departmentService';
import { SupervisionItem, SupervisionStatus, UrgencyLevel, SupervisionType } from '@/types';
import './SupervisionForm.css';

const { TextArea } = Input;
const { Option } = Select;

interface SupervisionFormData {
  title: string;
  description?: string;
  type: SupervisionType;
  urgency: UrgencyLevel;
  status: SupervisionStatus;
  deadline: dayjs.Dayjs;
  assignee_id?: number;
  creator_department_id?: number;
  responsible_department_id?: number;
  source: string;
  requirements?: string;
  expected_result?: string;
  is_key_supervision: boolean;
  estimated_hours?: number;
  files?: any[];
}

const SupervisionForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [form] = Form.useForm<SupervisionFormData>();
  const [loading, setLoading] = useState(false);

  const isEdit = !!id;

  // 获取督办事项详情（编辑模式）
  const { data: supervisionDetail, isLoading: detailLoading } = useQuery(
    ['supervision-detail', id],
    () => supervisionService.getSupervisionItem(id!),
    {
      enabled: isEdit,
      onSuccess: (data) => {
        const item = data.data;
        form.setFieldsValue({
          title: item.title,
          description: item.description,
          type: item.type as SupervisionType,
          urgency: item.urgency as UrgencyLevel,
          status: item.status as SupervisionStatus,
          deadline: dayjs(item.deadline),
          assignee_id: item.assignee_id ? parseInt(item.assignee_id) : undefined,
          creator_department_id: item.creator_department_id ? parseInt(item.creator_department_id) : undefined,
          responsible_department_id: item.responsible_department_id ? parseInt(item.responsible_department_id) : undefined,
          source: item.source,
          requirements: item.requirements,
          expected_result: item.expected_result,
          is_key_supervision: item.type === 'key',
          estimated_hours: item.estimated_hours
        });
      }
    }
  );

  // 获取用户列表
  const { data: usersData } = useQuery(
    'users-list',
    () => userService.getUsers({ page: 1, size: 1000 })
  );

  // 获取部门列表
  const { data: departmentsData } = useQuery(
    'departments-list',
    () => departmentService.getDepartmentList({ page: 1, size: 1000 })
  );

  // 创建督办事项
  const createMutation = useMutation(
    (data: any) => supervisionService.createSupervisionItem(data),
    {
      onSuccess: () => {
        message.success('创建成功');
        queryClient.invalidateQueries('supervision-list');
        navigate('/supervision/list');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '创建失败');
      }
    }
  );

  // 更新督办事项
  const updateMutation = useMutation(
    (data: any) => supervisionService.updateSupervisionItem(id!, data),
    {
      onSuccess: () => {
        message.success('更新成功');
        queryClient.invalidateQueries('supervision-list');
        queryClient.invalidateQueries(['supervision-detail', id]);
        navigate('/supervision/list');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '更新失败');
      }
    }
  );

  // 处理表单提交
  const handleSubmit = async (values: SupervisionFormData) => {
    setLoading(true);
    try {
      const submitData = {
        ...values,
        deadline: values.deadline.format('YYYY-MM-DD HH:mm:ss'),
        type: values.is_key_supervision ? 'key' : values.type
      };

      if (isEdit) {
        updateMutation.mutate(submitData);
      } else {
        createMutation.mutate(submitData);
      }
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setLoading(false);
    }
  };

  // 保存草稿
  const handleSaveDraft = async () => {
    try {
      const values = await form.validateFields();
      const submitData = {
        ...values,
        deadline: values.deadline.format('YYYY-MM-DD HH:mm:ss'),
        status: 'draft' as SupervisionStatus,
        type: values.is_key_supervision ? 'key' : values.type
      };

      if (isEdit) {
        updateMutation.mutate(submitData);
      } else {
        createMutation.mutate(submitData);
      }
    } catch (error) {
      console.error('Save draft error:', error);
    }
  };

  const users = usersData?.data?.items || [];
  const departments = departmentsData?.data?.items || [];

  if (isEdit && detailLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="supervision-form">
      <Card
        title={
          <Space>
            <Button 
              type="text" 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/supervision/list')}
            />
            {isEdit ? '编辑督办事项' : '创建督办事项'}
          </Space>
        }
        extra={
          <Space>
            <Button onClick={handleSaveDraft} loading={loading}>
              保存草稿
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={() => form.submit()}
              loading={loading}
            >
              {isEdit ? '更新' : '创建'}
            </Button>
          </Space>
        }
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            type: 'regular',
            urgency: 'medium',
            status: 'pending',
            is_key_supervision: false,
            source: '上级督办'
          }}
        >
          <Row gutter={24}>
            {/* 基本信息 */}
            <Col span={24}>
              <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                  <Col span={24}>
                    <Form.Item
                      name="title"
                      label="督办事项标题"
                      rules={[
                        { required: true, message: '请输入督办事项标题' },
                        { max: 200, message: '标题不能超过200个字符' }
                      ]}
                    >
                      <Input 
                        placeholder="请输入督办事项标题"
                        prefix={<FileTextOutlined />}
                      />
                    </Form.Item>
                  </Col>
                  
                  <Col span={24}>
                    <Form.Item
                      name="description"
                      label="详细描述"
                      rules={[{ max: 2000, message: '描述不能超过2000个字符' }]}
                    >
                      <TextArea
                        rows={4}
                        placeholder="请详细描述督办事项的具体内容、背景和要求"
                      />
                    </Form.Item>
                  </Col>

                  <Col span={8}>
                    <Form.Item
                      name="type"
                      label="督办类型"
                      rules={[{ required: true, message: '请选择督办类型' }]}
                    >
                      <Select placeholder="请选择督办类型">
                        <Option value="regular">常规督办</Option>
                        <Option value="key">重点督办</Option>
                        <Option value="special">专项督办</Option>
                        <Option value="emergency">应急督办</Option>
                      </Select>
                    </Form.Item>
                  </Col>

                  <Col span={8}>
                    <Form.Item
                      name="urgency"
                      label="紧急程度"
                      rules={[{ required: true, message: '请选择紧急程度' }]}
                    >
                      <Select placeholder="请选择紧急程度">
                        <Option value="low">一般</Option>
                        <Option value="medium">急办</Option>
                        <Option value="high">特急</Option>
                      </Select>
                    </Form.Item>
                  </Col>

                  <Col span={8}>
                    <Form.Item
                      name="status"
                      label="当前状态"
                      rules={[{ required: true, message: '请选择当前状态' }]}
                    >
                      <Select placeholder="请选择当前状态">
                        <Option value="draft">草稿</Option>
                        <Option value="pending">待办</Option>
                        <Option value="in_progress">进行中</Option>
                        <Option value="completed">已完成</Option>
                        <Option value="suspended">暂停</Option>
                        <Option value="cancelled">已取消</Option>
                      </Select>
                    </Form.Item>
                  </Col>

                  <Col span={12}>
                    <Form.Item
                      name="deadline"
                      label="截止时间"
                      rules={[{ required: true, message: '请选择截止时间' }]}
                    >
                      <DatePicker
                        showTime
                        format="YYYY-MM-DD HH:mm"
                        placeholder="请选择截止时间"
                        style={{ width: '100%' }}
                        disabledDate={(current) => current && current < dayjs().startOf('day')}
                      />
                    </Form.Item>
                  </Col>

                  <Col span={12}>
                    <Form.Item
                      name="estimated_hours"
                      label="预估工时（小时）"
                    >
                      <InputNumber
                        min={0}
                        placeholder="预估完成所需工时"
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>

                  <Col span={24}>
                    <Form.Item
                      name="is_key_supervision"
                      label="重点督办"
                      valuePropName="checked"
                    >
                      <Switch
                        checkedChildren="是"
                        unCheckedChildren="否"
                        onChange={(checked) => {
                          if (checked) {
                            form.setFieldsValue({ type: SupervisionType.KEY });
                          }
                        }}
                      />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>

            {/* 责任信息 */}
            <Col span={24}>
              <Card title="责任信息" size="small" style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                  <Col span={8}>
                    <Form.Item
                      name="assignee_id"
                      label="责任人"
                      rules={[{ required: true, message: '请选择责任人' }]}
                    >
                      <Select
                        placeholder="请选择责任人"
                        showSearch
                        filterOption={(input: string, option: any) =>
                          option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                        }
                      >
                        {users.map((user: any) => (
                          <Option key={user.id} value={user.id}>
                            <Space>
                              <UserOutlined />
                              {user.real_name || user.username}
                              {user.department && (
                                <Tag>{user.department.name}</Tag>
                              )}
                            </Space>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>

                  <Col span={8}>
                    <Form.Item
                      name="creator_department_id"
                      label="督办部门"
                    >
                      <Select placeholder="请选择督办部门">
                        {departments.map((dept: any) => (
                          <Option key={dept.id} value={dept.id}>
                            <Space>
                              <BankOutlined />
                              {dept.name}
                            </Space>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>

                  <Col span={8}>
                    <Form.Item
                      name="responsible_department_id"
                      label="责任部门"
                      rules={[{ required: true, message: '请选择责任部门' }]}
                    >
                      <Select placeholder="请选择责任部门">
                        {departments.map((dept: any) => (
                          <Option key={dept.id} value={dept.id}>
                            <Space>
                              <BankOutlined />
                              {dept.name}
                            </Space>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>

            {/* 督办要求 */}
            <Col span={24}>
              <Card title="督办要求" size="small" style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      name="source"
                      label="督办来源"
                      rules={[{ required: true, message: '请输入督办来源' }]}
                    >
                      <Input placeholder="如：市政府、上级部门等" />
                    </Form.Item>
                  </Col>

                  <Col span={24}>
                    <Form.Item
                      name="requirements"
                      label="具体要求"
                    >
                      <TextArea
                        rows={3}
                        placeholder="请详细描述督办的具体要求和标准"
                      />
                    </Form.Item>
                  </Col>

                  <Col span={24}>
                    <Form.Item
                      name="expected_result"
                      label="预期结果"
                    >
                      <TextArea
                        rows={3}
                        placeholder="请描述期望达到的结果和效果"
                      />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
        </Form>
      </Card>
    </div>
  );
};

export default SupervisionForm;