import { request } from './api';
import { LoginResponse, User } from '@/types';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface RegisterRequest {
  username: string;
  real_name: string;
  password: string;
  email?: string;
  phone?: string;
  employee_id?: string;
  position?: string;
  department_id?: string;
}

export const authService = {
  // 用户登录
  login: (data: LoginRequest) => {
    return request.post<LoginResponse>('/auth/login', data);
  },
  
  // 刷新token
  refreshToken: (refreshToken: string) => {
    return request.post<{ access_token: string; token_type: string; expires_in: number }>('/auth/refresh', {
      refresh_token: refreshToken,
    });
  },
  
  // 用户注册
  register: (data: RegisterRequest) => {
    return request.post<User>('/auth/register', data);
  },
  
  // 获取当前用户信息
  getCurrentUser: () => {
    return request.get<User>('/auth/me');
  },
  
  // 用户登出
  logout: () => {
    return request.post('/auth/logout');
  },
  
  // 修改密码
  changePassword: (data: ChangePasswordRequest) => {
    return request.post('/auth/change-password', data);
  },
  
  // 忘记密码
  forgotPassword: (email: string) => {
    return request.post('/auth/forgot-password', { email });
  },
  
  // 重置密码
  resetPassword: (token: string, newPassword: string) => {
    return request.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
  },
};