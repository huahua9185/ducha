import { request } from './api';
import { User, UserCreate, UserUpdate, PaginatedResponse } from '@/types';

export interface UserListParams {
  page?: number;
  size?: number;
  search?: string;
  department_id?: string;
  is_active?: boolean;
}

export const userService = {
  // 获取用户列表
  getUsers: (params?: UserListParams) => {
    const queryParams = new URLSearchParams();
    
    if (params?.page) queryParams.append('skip', String((params.page - 1) * (params.size || 20)));
    if (params?.size) queryParams.append('limit', String(params.size));
    if (params?.search) queryParams.append('search', params.search);
    if (params?.department_id) queryParams.append('department_id', params.department_id);
    if (params?.is_active !== undefined) queryParams.append('is_active', String(params.is_active));
    
    return request.get<PaginatedResponse<User>>(`/users?${queryParams.toString()}`);
  },
  
  // 获取用户详情
  getUser: (userId: string) => {
    return request.get<User>(`/users/${userId}`);
  },
  
  // 创建用户
  createUser: (data: UserCreate) => {
    return request.post<User>('/users', data);
  },
  
  // 更新用户
  updateUser: (userId: string, data: UserUpdate) => {
    return request.put<User>(`/users/${userId}`, data);
  },
  
  // 删除用户
  deleteUser: (userId: string) => {
    return request.delete(`/users/${userId}`);
  },
  
  // 激活用户
  activateUser: (userId: string) => {
    return request.post(`/users/${userId}/activate`);
  },
  
  // 停用用户
  deactivateUser: (userId: string) => {
    return request.post(`/users/${userId}/deactivate`);
  },
  
  // 分配用户角色
  assignUserRoles: (userId: string, roleIds: string[]) => {
    return request.post<User>(`/users/${userId}/roles`, {
      user_id: userId,
      role_ids: roleIds,
    });
  },
  
  // 获取用户下属
  getUserSubordinates: (userId: string) => {
    return request.get<User[]>(`/users/${userId}/subordinates`);
  },
  
  // 获取部门列表
  getDepartments: () => {
    return request.get('/departments');
  },
};