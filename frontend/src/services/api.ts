import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { message } from 'antd';
import { useAuthStore } from '@/store/authStore';
import { ApiResponse } from '@/types';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config: any) => {
    // 获取token
    const token = useAuthStore.getState().token;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 直接返回响应数据
    return response;
  },
  async (error) => {
    const { response } = error;
    
    if (response) {
      const { status, data } = response;
      
      switch (status) {
        case 401:
          // Token过期或无效，尝试刷新token
          const refreshToken = useAuthStore.getState().refreshToken;
          if (refreshToken) {
            try {
              const refreshResponse = await api.post('/auth/refresh', {
                refresh_token: refreshToken,
              });
              
              const { access_token } = refreshResponse.data.data;
              useAuthStore.getState().setToken(access_token);
              
              // 重新发送原始请求
              const originalRequest = error.config;
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return api(originalRequest);
            } catch (refreshError) {
              // 刷新失败，清除认证信息并跳转到登录页
              useAuthStore.getState().logout();
              window.location.href = '/login';
              message.error('登录已过期，请重新登录');
            }
          } else {
            useAuthStore.getState().logout();
            window.location.href = '/login';
            message.error('请先登录');
          }
          break;
          
        case 403:
          message.error(data?.message || '权限不足');
          break;
          
        case 404:
          message.error(data?.message || '请求的资源不存在');
          break;
          
        case 422:
          message.error(data?.message || '请求参数验证失败');
          break;
          
        case 500:
          message.error(data?.message || '服务器内部错误');
          break;
          
        default:
          message.error(data?.message || '请求失败');
      }
    } else {
      // 网络错误
      message.error('网络连接失败，请检查网络设置');
    }
    
    return Promise.reject(error);
  }
);

// 通用请求方法
export const request = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    return api.get(url, config).then(res => res.data);
  },
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    return api.post(url, data, config).then(res => res.data);
  },
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    return api.put(url, data, config).then(res => res.data);
  },
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    return api.delete(url, config).then(res => res.data);
  },
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    return api.patch(url, data, config).then(res => res.data);
  },
};

export default api;