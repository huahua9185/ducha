import { create } from 'zustand';

interface AppState {
  // 侧边栏状态
  sidebarCollapsed: boolean;
  
  // 主题设置
  theme: 'light' | 'dark';
  
  // 语言设置
  locale: 'zh-CN' | 'en-US';
  
  // 页面加载状态
  loading: boolean;
  
  // 面包屑
  breadcrumb: Array<{ title: string; path?: string }>;
  
  // 动作
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setLocale: (locale: 'zh-CN' | 'en-US') => void;
  setLoading: (loading: boolean) => void;
  setBreadcrumb: (breadcrumb: Array<{ title: string; path?: string }>) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // 初始状态
  sidebarCollapsed: false,
  theme: 'light',
  locale: 'zh-CN',
  loading: false,
  breadcrumb: [],
  
  // 切换侧边栏
  toggleSidebar: () => {
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  },
  
  // 设置侧边栏状态
  setSidebarCollapsed: (collapsed: boolean) => {
    set({ sidebarCollapsed: collapsed });
  },
  
  // 设置主题
  setTheme: (theme: 'light' | 'dark') => {
    set({ theme });
  },
  
  // 设置语言
  setLocale: (locale: 'zh-CN' | 'en-US') => {
    set({ locale });
  },
  
  // 设置加载状态
  setLoading: (loading: boolean) => {
    set({ loading });
  },
  
  // 设置面包屑
  setBreadcrumb: (breadcrumb: Array<{ title: string; path?: string }>) => {
    set({ breadcrumb });
  },
}));