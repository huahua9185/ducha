import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';

interface AuthState {
  // 状态
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  
  // 动作
  login: (token: string, refreshToken: string, user: User) => void;
  logout: () => void;
  updateUser: (user: User) => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      isAuthenticated: false,
      user: null,
      token: null,
      refreshToken: null,
      
      // 登录
      login: (token: string, refreshToken: string, user: User) => {
        set({
          isAuthenticated: true,
          token,
          refreshToken,
          user,
        });
      },
      
      // 登出
      logout: () => {
        set({
          isAuthenticated: false,
          user: null,
          token: null,
          refreshToken: null,
        });
      },
      
      // 更新用户信息
      updateUser: (user: User) => {
        set({ user });
      },
      
      // 设置新的访问令牌
      setToken: (token: string) => {
        set({ token });
      },
    }),
    {
      name: 'auth-storage',
      // 选择要持久化的字段
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
      }),
    }
  )
);