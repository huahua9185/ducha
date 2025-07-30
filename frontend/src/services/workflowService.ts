import { apiClient } from './apiClient';

// 工作流状态枚举
export enum WorkflowStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  COMPLETED = 'completed',
  TERMINATED = 'terminated'
}

// 节点状态枚举
export enum NodeStatus {
  PENDING = 'pending',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  SKIPPED = 'skipped',
  FAILED = 'failed'
}

// 节点类型枚举
export enum NodeType {
  START = 'start',
  END = 'end',
  TASK = 'task',
  DECISION = 'decision',
  PARALLEL = 'parallel',
  MERGE = 'merge'
}

// 工作流模板接口
export interface WorkflowTemplate {
  id: string;
  name: string;
  code: string;
  description?: string;
  type: string;
  version: string;
  is_enabled: boolean;
  is_builtin: boolean;
  definition: any;
  form_config?: any;
  permission_config?: any;
  notification_config?: any;
  sort_order: number;
  created_at: string;
  updated_at?: string;
}

// 工作流实例接口
export interface WorkflowInstance {
  id: string;
  number: string;
  title: string;
  template_id: string;
  initiator_id: string;
  business_id?: string;
  business_type?: string;
  status: WorkflowStatus;
  current_nodes?: string[];
  start_time?: string;
  end_time?: string;
  business_data?: any;
  variables?: any;
  priority: number;
  created_at: string;
  updated_at?: string;
}

// 工作流节点接口
export interface WorkflowNode {
  id: string;
  workflow_instance_id: string;
  node_id: string;
  name: string;
  type: NodeType;
  status: NodeStatus;
  assignee_id?: string;
  assignee_role_id?: string;
  assignee_department_id?: string;
  processor_id?: string;
  enter_time?: string;
  start_time?: string;
  complete_time?: string;
  deadline?: string;
  node_data?: any;
  form_data?: any;
  comment?: string;
  created_at: string;
  updated_at?: string;
}

// 查询参数接口
export interface WorkflowTemplateQuery {
  page?: number;
  size?: number;
  keyword?: string;
  type_filter?: string;
  is_enabled?: boolean;
}

export interface WorkflowInstanceQuery {
  page?: number;
  size?: number;
  keyword?: string;
  status_filter?: WorkflowStatus;
  template_id?: string;
  business_type?: string;
}

export interface TaskQuery {
  page?: number;
  size?: number;
  status_filter?: NodeStatus;
}

// 创建/更新参数接口
export interface CreateWorkflowTemplateData {
  name: string;
  code: string;
  description?: string;
  type: string;
  version?: string;
  is_enabled?: boolean;
  definition: any;
  form_config?: any;
  permission_config?: any;
  notification_config?: any;
  sort_order?: number;
}

export interface UpdateWorkflowTemplateData {
  name?: string;
  description?: string;
  is_enabled?: boolean;
  definition?: any;
  form_config?: any;
  permission_config?: any;
  notification_config?: any;
  sort_order?: number;
}

export interface CreateWorkflowInstanceData {
  title: string;
  template_id: string;
  business_id?: string;
  business_type?: string;
  business_data?: any;
  variables?: any;
  priority?: number;
}

export interface TaskCompleteData {
  form_data?: any;
  comment?: string;
  result?: string;
}

// 统计信息接口
export interface WorkflowStats {
  total_templates: number;
  active_templates: number;
  total_instances: number;
  running_instances: number;
  completed_instances: number;
  pending_tasks: number;
  overdue_tasks: number;
}

export interface UserTaskStats {
  pending_tasks: number;
  processing_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
}

// 工作流服务
export const workflowService = {
  // ========== 工作流模板管理 ==========
  
  // 获取工作流模板列表
  getTemplateList: (params: WorkflowTemplateQuery): Promise<{ data: any }> => {
    return apiClient.get('/workflow/templates', { params });
  },

  // 获取工作流模板详情
  getTemplate: (id: string): Promise<{ data: WorkflowTemplate }> => {
    return apiClient.get(`/workflow/templates/${id}`);
  },

  // 创建工作流模板
  createTemplate: (data: CreateWorkflowTemplateData): Promise<{ data: WorkflowTemplate }> => {
    return apiClient.post('/workflow/templates', data);
  },

  // 更新工作流模板
  updateTemplate: (id: string, data: UpdateWorkflowTemplateData): Promise<{ data: WorkflowTemplate }> => {
    return apiClient.put(`/workflow/templates/${id}`, data);
  },

  // 删除工作流模板
  deleteTemplate: (id: string): Promise<{ data: any }> => {
    return apiClient.delete(`/workflow/templates/${id}`);
  },

  // ========== 工作流实例管理 ==========

  // 获取工作流实例列表
  getInstanceList: (params: WorkflowInstanceQuery): Promise<{ data: any }> => {
    return apiClient.get('/workflow/instances', { params });
  },

  // 获取工作流实例详情
  getInstance: (id: string): Promise<{ data: WorkflowInstance }> => {
    return apiClient.get(`/workflow/instances/${id}`);
  },

  // 创建工作流实例
  createInstance: (data: CreateWorkflowInstanceData): Promise<{ data: WorkflowInstance }> => {
    return apiClient.post('/workflow/instances', data);
  },

  // 启动工作流实例
  startInstance: (id: string): Promise<{ data: any }> => {
    return apiClient.post(`/workflow/instances/${id}/start`);
  },

  // ========== 任务管理 ==========

  // 获取我的待办任务
  getMyTasks: (params: TaskQuery): Promise<{ data: any }> => {
    return apiClient.get('/workflow/my-tasks', { params });
  },

  // 完成任务
  completeTask: (taskId: string, data: TaskCompleteData): Promise<{ data: any }> => {
    return apiClient.post(`/workflow/tasks/${taskId}/complete`, data);
  },

  // ========== 统计信息 ==========

  // 获取工作流统计信息
  getStats: (): Promise<{ data: WorkflowStats }> => {
    return apiClient.get('/workflow/stats');
  },

  // 获取用户任务统计
  getUserTaskStats: (): Promise<{ data: UserTaskStats }> => {
    return apiClient.get('/workflow/user-stats');
  }
};