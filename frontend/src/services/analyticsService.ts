import { apiClient } from './apiClient';

export interface AnalyticsQuery {
  start_date: string;
  end_date: string;
  department_id?: number;
  type?: string;
  urgency?: string;
}

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

export interface TypeStats {
  type: string;
  count: number;
  completion_rate: number;
}

export interface UrgencyStats {
  urgency: string;
  count: number;
  completion_rate: number;
}

export interface MonthlyTrend {
  month: string;
  created: number;
  completed: number;
  completion_rate: number;
}

export interface AnalyticsOverviewResponse {
  summary: AnalyticsSummary;
  department_stats: DepartmentStats[];
  type_stats: TypeStats[];
  urgency_stats: UrgencyStats[];
  monthly_trend: MonthlyTrend[];
}

export const analyticsService = {
  // 获取分析概览
  getAnalyticsOverview: (params: AnalyticsQuery): Promise<{ data: AnalyticsOverviewResponse }> => {
    return apiClient.get('/analytics/overview', { params });
  },

  // 获取效能分析
  getEfficiencyAnalysis: (params: AnalyticsQuery): Promise<{ data: any }> => {
    return apiClient.get('/analytics/efficiency', { params });
  },

  // 获取部门分析
  getDepartmentAnalysis: (params: AnalyticsQuery): Promise<{ data: any }> => {
    return apiClient.get('/analytics/department', { params });
  },

  // 获取趋势分析
  getTrendAnalysis: (params: AnalyticsQuery): Promise<{ data: any }> => {
    return apiClient.get('/analytics/trend', { params });
  },

  // 导出统计报告
  exportReport: (params: AnalyticsQuery): Promise<Blob> => {
    return apiClient.get('/analytics/export', { 
      params,
      responseType: 'blob'
    });
  },

  // 获取实时统计
  getRealtimeStats: (): Promise<{ data: any }> => {
    return apiClient.get('/analytics/realtime');
  }
};