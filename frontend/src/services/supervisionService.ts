import { request } from './api';
import { SupervisionItem, PaginatedResponse } from '@/types';

export interface SupervisionItemCreate {
  title: string;
  content: string;
  type: 'regular' | 'emergency' | 'key' | 'follow_up';
  urgency: 'low' | 'medium' | 'high';
  responsible_department_id: string;
  cooperating_departments?: string[];
  source?: string;
  start_date: string;
  deadline: string;
  expected_result?: string;
  is_public: boolean;
  is_key: boolean;
  tags?: string[];
}

export interface SupervisionItemUpdate {
  title?: string;
  content?: string;
  type?: 'regular' | 'emergency' | 'key' | 'follow_up';
  urgency?: 'low' | 'medium' | 'high';
  responsible_department_id?: string;
  cooperating_departments?: string[];
  source?: string;
  start_date?: string;
  deadline?: string;
  expected_result?: string;
  actual_result?: string;
  is_public?: boolean;
  is_key?: boolean;
  tags?: string[];
  status?: 'draft' | 'pending' | 'in_progress' | 'completed' | 'overdue' | 'suspended' | 'cancelled';
}

export interface SupervisionListParams {
  page?: number;
  size?: number;
  search?: string;
  type?: 'regular' | 'emergency' | 'key' | 'follow_up';
  status?: 'draft' | 'pending' | 'in_progress' | 'completed' | 'overdue' | 'suspended' | 'cancelled';
  urgency?: 'low' | 'medium' | 'high';
  creator_id?: string;
  responsible_department_id?: string;
  is_key?: boolean;
  start_date_from?: string;
  start_date_to?: string;
  deadline_from?: string;
  deadline_to?: string;
}

export interface TaskAssignmentCreate {
  title: string;
  description?: string;
  assignee_id: string;
  assigned_department_id?: string;
  priority: number;
  start_date?: string;
  deadline: string;
  estimated_hours?: number;
  notes?: string;
}

export interface ProgressReportCreate {
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

export interface SupervisionEvaluation {
  quality_score: number;
  efficiency_score: number;
  satisfaction_score: number;
  evaluation_comment?: string;
}

export const supervisionService = {
  // 督办事项管理
  getSupervisionItems: (params?: SupervisionListParams) => {
    const queryParams = new URLSearchParams();
    
    if (params?.page) queryParams.append('skip', String((params.page - 1) * (params.size || 20)));
    if (params?.size) queryParams.append('limit', String(params.size));
    if (params?.search) queryParams.append('search', params.search);
    if (params?.type) queryParams.append('type', params.type);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.urgency) queryParams.append('urgency', params.urgency);
    if (params?.creator_id) queryParams.append('creator_id', params.creator_id);
    if (params?.responsible_department_id) queryParams.append('responsible_department_id', params.responsible_department_id);
    if (params?.is_key !== undefined) queryParams.append('is_key', String(params.is_key));
    if (params?.start_date_from) queryParams.append('start_date_from', params.start_date_from);
    if (params?.start_date_to) queryParams.append('start_date_to', params.start_date_to);
    if (params?.deadline_from) queryParams.append('deadline_from', params.deadline_from);
    if (params?.deadline_to) queryParams.append('deadline_to', params.deadline_to);
    
    return request.get<PaginatedResponse<SupervisionItem>>(`/supervision?${queryParams.toString()}`);
  },

  getSupervisionItem: (itemId: string) => {
    return request.get<SupervisionItem>(`/supervision/${itemId}`);
  },

  createSupervisionItem: (data: SupervisionItemCreate) => {
    return request.post<SupervisionItem>('/supervision', data);
  },

  updateSupervisionItem: (itemId: string, data: SupervisionItemUpdate) => {
    return request.put<SupervisionItem>(`/supervision/${itemId}`, data);
  },

  deleteSupervisionItem: (itemId: string) => {
    return request.delete(`/supervision/${itemId}`);
  },

  changeSupervisionStatus: (itemId: string, newStatus: string, reason?: string) => {
    return request.post(`/supervision/${itemId}/status`, {
      new_status: newStatus,
      reason,
    });
  },

  evaluateSupervisionItem: (itemId: string, evaluation: SupervisionEvaluation) => {
    return request.post(`/supervision/${itemId}/evaluate`, evaluation);
  },

  // 任务分配管理
  getTaskAssignments: (itemId: string) => {
    return request.get(`/supervision/${itemId}/tasks`);
  },

  createTaskAssignment: (itemId: string, data: TaskAssignmentCreate) => {
    return request.post(`/supervision/${itemId}/tasks`, data);
  },

  updateTaskAssignment: (taskId: string, data: any) => {
    return request.put(`/supervision/tasks/${taskId}`, data);
  },

  acceptTaskAssignment: (taskId: string) => {
    return request.post(`/supervision/tasks/${taskId}/accept`);
  },

  completeTaskAssignment: (taskId: string, actualHours?: number) => {
    return request.post(`/supervision/tasks/${taskId}/complete`, {
      actual_hours: actualHours,
    });
  },

  // 进度报告管理
  getProgressReports: (itemId: string, page = 1, size = 20) => {
    return request.get(`/supervision/${itemId}/reports?skip=${(page - 1) * size}&limit=${size}`);
  },

  createProgressReport: (itemId: string, data: ProgressReportCreate) => {
    return request.post(`/supervision/${itemId}/reports`, data);
  },

  updateProgressReport: (reportId: string, data: any) => {
    return request.put(`/supervision/reports/${reportId}`, data);
  },

  // 状态日志
  getStatusLogs: (itemId: string) => {
    return request.get(`/supervision/${itemId}/logs`);
  },

  // 统计数据
  getSupervisionStats: (departmentId?: string) => {
    const params = departmentId ? `?department_id=${departmentId}` : '';
    return request.get(`/supervision/stats/overview${params}`);
  },

  getDepartmentStats: () => {
    return request.get('/supervision/stats/departments');
  },

  getOverdueItems: (limit = 50) => {
    return request.get<SupervisionItem[]>(`/supervision/overdue?limit=${limit}`);
  },

  getUrgentItems: (limit = 50) => {
    return request.get<SupervisionItem[]>(`/supervision/urgent?limit=${limit}`);
  },
};