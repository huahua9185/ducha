// 枚举类型定义
export enum SupervisionStatus {
  DRAFT = 'draft',
  PENDING = 'pending', 
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  OVERDUE = 'overdue',
  SUSPENDED = 'suspended',
  CANCELLED = 'cancelled'
}

export enum UrgencyLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high'
}

export enum SupervisionType {
  REGULAR = 'regular',
  EMERGENCY = 'emergency',
  KEY = 'key',
  FOLLOW_UP = 'follow_up'
}

// 用户相关类型
export interface User {
  id: string;
  username: string;
  real_name: string;
  email?: string;
  phone?: string;
  employee_id?: string;
  position?: string;
  department_id?: string;
  superior_id?: string;
  avatar_url?: string;
  bio?: string;
  work_years?: number;
  address?: string;
  is_active: boolean;
  is_superuser: boolean;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  real_name: string;
  password: string;
  email?: string;
  phone?: string;
  employee_id?: string;
  position?: string;
  department_id?: string;
  superior_id?: string;
  avatar_url?: string;
  bio?: string;
  work_years?: number;
  address?: string;
}

export interface UserUpdate {
  real_name?: string;
  email?: string;
  phone?: string;
  employee_id?: string;
  position?: string;
  department_id?: string;
  superior_id?: string;
  avatar_url?: string;
  bio?: string;
  work_years?: number;
  address?: string;
  is_active?: boolean;
  password?: string;
}

// 角色相关类型
export interface Role {
  id: string;
  name: string;
  code: string;
  description?: string;
  is_builtin: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

// 权限相关类型
export interface Permission {
  id: string;
  name: string;
  code: string;
  description?: string;
  type: string;
  parent_id?: string;
  path?: string;
  icon?: string;
  sort_order: number;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}


// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  success: boolean;
}

// 登录响应类型
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// 菜单项类型
export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  children?: MenuItem[];
  permission?: string;
}

// 表格列类型
export interface TableColumn {
  title: string;
  dataIndex: string;
  key: string;
  width?: number;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, record: any, index: number) => React.ReactNode;
  sorter?: boolean;
  filters?: Array<{ text: string; value: any }>;
}

// 表单字段类型
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'date' | 'number' | 'checkbox' | 'radio';
  required?: boolean;
  placeholder?: string;
  options?: Array<{ label: string; value: any }>;
  rules?: any[];
}

// 统计数据类型
export interface StatisticData {
  title: string;
  value: number;
  suffix?: string;
  precision?: number;
  valueStyle?: React.CSSProperties;
  prefix?: React.ReactNode;
}

// 部门相关类型
export interface Department {
  id: string;
  name: string;
  code: string;
  short_name?: string;
  organization_id: string;
  parent_id?: string;
  path?: string;
  level: number;
  type: string;
  function_desc?: string;
  manager_id?: string;
  phone?: string;
  fax?: string;
  email?: string;
  address?: string;
  sort_order: number;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

// 督办事项相关类型
export interface SupervisionItem {
  id: string;
  number: string;
  title: string;
  content: string;
  description?: string;
  type: SupervisionType;
  status: SupervisionStatus;
  urgency: UrgencyLevel;
  source?: string;
  start_date: string;
  deadline: string;
  actual_completion_date?: string;
  completion_rate: number;
  expected_result?: string;
  actual_result?: string;
  quality_score?: number;
  efficiency_score?: number;
  satisfaction_score?: number;
  overall_score?: number;
  evaluation_comment?: string;
  is_public: boolean;
  is_key: boolean;
  tags?: string[];
  creator_id: string;
  responsible_department_id: string;
  cooperating_departments?: string[];
  assignee_id?: string;
  creator_department_id?: string;
  requirements?: string;
  estimated_hours?: number;
  assignee?: User;
  responsible_department?: Department;
  creator_department?: Department;
  created_at: string;
  updated_at: string;
}

// 图表数据类型
export interface ChartData {
  name: string;
  value: number;
  [key: string]: any;
}

// 工作流相关类型
export enum WorkflowStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  COMPLETED = 'completed',
  TERMINATED = 'terminated'
}

export enum NodeStatus {
  PENDING = 'pending',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  SKIPPED = 'skipped',
  FAILED = 'failed'
}

export enum NodeType {
  START = 'start',
  END = 'end',
  TASK = 'task',
  DECISION = 'decision',
  PARALLEL = 'parallel',
  MERGE = 'merge'
}

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
  workflow_instance?: WorkflowInstance;
  created_at: string;
  updated_at?: string;
}

// 部门相关类型
export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
  parent_id?: string;
  level: number;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 监控预警相关类型
export interface MonitoringAlert {
  id: number;
  supervision_item_id: number;
  alert_type: 'overdue' | 'deadline_approaching' | 'slow_progress' | 'high_workload' | 'quality_issue';
  alert_level: 'normal' | 'attention' | 'warning' | 'critical';
  title: string;
  message: string;
  created_at: string;
  is_resolved: boolean;
  supervision_item: {
    id: number;
    title: string;
    number: string;
    status: string;
    deadline: string;
  };
}

// 统计分析相关类型
export interface AnalyticsSummary {
  total_items: number;
  completed_items: number;
  in_progress_items: number;
  overdue_items: number;
  completion_rate: number;
  average_completion_days: number;
  efficiency_score: number;
}

export interface DepartmentStats {
  department_id: number;
  department_name: string;
  total_items: number;
  completed_items: number;
  completion_rate: number;
  average_efficiency_score: number;
}