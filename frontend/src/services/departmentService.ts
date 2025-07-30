import { apiClient } from './apiClient';

export interface Department {
  id: number;
  name: string;
  code: string;
  description?: string;
  parent_id?: number;
  parent?: Department;
  children?: Department[];
  level: number;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DepartmentQuery {
  page: number;
  size: number;
  keyword?: string;
  parent_id?: number;
  is_active?: boolean;
}

export interface CreateDepartmentData {
  name: string;
  code: string;
  description?: string;
  parent_id?: number;
  sort_order?: number;
  is_active?: boolean;
}

export interface UpdateDepartmentData {
  name?: string;
  code?: string;
  description?: string;
  parent_id?: number;
  sort_order?: number;
  is_active?: boolean;
}

export const departmentService = {
  // 获取部门列表
  getDepartmentList: (params: DepartmentQuery): Promise<{ data: { items: Department[]; total: number } }> => {
    return apiClient.get('/departments', { params });
  },

  // 获取部门树形结构
  getDepartmentTree: (): Promise<{ data: Department[] }> => {
    return apiClient.get('/departments/tree');
  },

  // 获取部门详情
  getDepartmentById: (id: number): Promise<{ data: Department }> => {
    return apiClient.get(`/departments/${id}`);
  },

  // 创建部门
  createDepartment: (data: CreateDepartmentData): Promise<{ data: Department }> => {
    return apiClient.post('/departments', data);
  },

  // 更新部门
  updateDepartment: (id: number, data: UpdateDepartmentData): Promise<{ data: Department }> => {
    return apiClient.put(`/departments/${id}`, data);
  },

  // 删除部门
  deleteDepartment: (id: number): Promise<{ data: any }> => {
    return apiClient.delete(`/departments/${id}`);
  },

  // 激活/禁用部门
  toggleDepartmentStatus: (id: number, isActive: boolean): Promise<{ data: Department }> => {
    return apiClient.put(`/departments/${id}/status`, { is_active: isActive });
  },

  // 移动部门
  moveDepartment: (id: number, parentId?: number): Promise<{ data: Department }> => {
    return apiClient.put(`/departments/${id}/move`, { parent_id: parentId });
  },

  // 获取部门用户统计
  getDepartmentUserStats: (id: number): Promise<{ data: any }> => {
    return apiClient.get(`/departments/${id}/user-stats`);
  }
};