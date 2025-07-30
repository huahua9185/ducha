import { apiClient } from './apiClient';

export interface MonitoringStats {
  total_alerts: number;
  critical_alerts: number;
  warning_alerts: number;
  attention_alerts: number;
  overdue_items: number;
  approaching_deadline_items: number;
  slow_progress_items: number;
  high_workload_items: number;
}

export interface AlertsQuery {
  level?: string;
  type?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  size?: number;
}

export const monitoringService = {
  // 获取监控统计数据
  getMonitoringStats: (): Promise<{ data: MonitoringStats }> => {
    return apiClient.get('/monitoring/stats');
  },

  // 获取预警列表
  getAlerts: (params: AlertsQuery): Promise<{ data: { items: any[]; total: number } }> => {
    return apiClient.get('/monitoring/alerts', { params });
  },

  // 标记预警为已处理
  resolveAlert: (alertId: number): Promise<{ data: any }> => {
    return apiClient.put(`/monitoring/alerts/${alertId}/resolve`);
  },

  // 获取风险评估
  getRiskAssessment: (): Promise<{ data: any }> => {
    return apiClient.get('/monitoring/risk-assessment');
  },

  // 获取实时监控数据
  getRealtimeData: (): Promise<{ data: any }> => {
    return apiClient.get('/monitoring/realtime');
  }
};