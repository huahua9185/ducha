from typing import Any, Dict, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.services import monitoring_service

router = APIRouter()


@router.get("/alerts")
def get_comprehensive_alerts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取综合预警信息"""
    alerts = monitoring_service.get_comprehensive_alerts(db)
    summary = monitoring_service.get_alert_summary(alerts)
    
    return {
        "alerts": alerts,
        "summary": summary
    }


@router.get("/alerts/summary")
def get_alert_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取预警摘要"""
    alerts = monitoring_service.get_comprehensive_alerts(db)
    summary = monitoring_service.get_alert_summary(alerts)
    
    return summary


@router.get("/alerts/overdue")
def get_overdue_alerts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取逾期预警"""
    overdue_items = monitoring_service.check_overdue_items(db)
    overdue_tasks = monitoring_service.check_task_overdue(db)
    
    return {
        "overdue_items": overdue_items,
        "overdue_tasks": overdue_tasks,
        "total_count": len(overdue_items) + len(overdue_tasks)
    }


@router.get("/alerts/upcoming")
def get_upcoming_deadline_alerts(
    db: Session = Depends(deps.get_db),
    days_ahead: int = Query(3, ge=1, le=30, description="提前天数"),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取即将到期预警"""
    upcoming_items = monitoring_service.check_upcoming_deadlines(db, days_ahead)
    
    return {
        "upcoming_items": upcoming_items,
        "days_ahead": days_ahead,
        "total_count": len(upcoming_items)
    }


@router.get("/alerts/slow-progress")
def get_slow_progress_alerts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取进度缓慢预警"""
    slow_items = monitoring_service.check_slow_progress_items(db)
    
    return {
        "slow_progress_items": slow_items,
        "total_count": len(slow_items)
    }


@router.get("/alerts/workload")
def get_high_workload_alerts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取高工作负荷预警"""
    high_workload_users = monitoring_service.check_high_workload_users(db)
    
    return {
        "high_workload_users": high_workload_users,
        "total_count": len(high_workload_users)
    }


@router.get("/alerts/urgent-no-progress")
def get_urgent_no_progress_alerts(
    db: Session = Depends(deps.get_db),
    hours_threshold: int = Query(24, ge=1, le=168, description="无进展小时阈值"),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取紧急事项无进展预警"""
    urgent_items = monitoring_service.check_urgent_items_without_progress(db, hours_threshold)
    
    return {
        "urgent_no_progress_items": urgent_items,
        "hours_threshold": hours_threshold,
        "total_count": len(urgent_items)
    }


@router.get("/alerts/quality-risks")
def get_quality_risk_alerts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取质量风险预警"""
    quality_risks = monitoring_service.check_quality_risks(db)
    
    return {
        "quality_risk_items": quality_risks,
        "total_count": len(quality_risks)
    }


@router.post("/alerts/schedule-monitoring")
def schedule_monitoring_tasks(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_system_config)
) -> Any:
    """执行定时监控任务"""
    alerts = monitoring_service.schedule_monitoring_tasks(db)
    summary = monitoring_service.get_alert_summary(alerts)
    
    return {
        "message": "监控任务执行完成",
        "alerts": alerts,
        "summary": summary
    }


@router.post("/status/update-overdue")
def update_overdue_status(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_system_config)
) -> Any:
    """更新逾期状态"""
    updated_count = monitoring_service.update_overdue_status(db)
    
    return {
        "message": f"已更新 {updated_count} 个逾期督办事项的状态",
        "updated_count": updated_count
    }


@router.get("/risk-analysis/department/{department_id}")
def get_department_risk_analysis(
    *,
    db: Session = Depends(deps.get_db),
    department_id: UUID,
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取部门风险分析"""
    risk_analysis = monitoring_service.get_department_risk_analysis(db, department_id)
    
    return risk_analysis


@router.get("/dashboard/overview")
def get_monitoring_dashboard_overview(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取监控仪表板概览"""
    alerts = monitoring_service.get_comprehensive_alerts(db)
    summary = monitoring_service.get_alert_summary(alerts)
    
    # 获取关键指标
    key_metrics = {
        "critical_alerts": summary["critical_count"],
        "warning_alerts": summary["warning_count"],
        "overdue_items": len(alerts["overdue_items"]),
        "urgent_items": len(alerts["urgent_no_progress"]),
        "high_workload_users": len(alerts["high_workload_users"]),
        "quality_risks": len(alerts["quality_risks"])
    }
    
    # 获取最新的关键预警
    critical_alerts = []
    for alert_type, alert_list in alerts.items():
        for alert in alert_list:
            if alert.get("level") == "critical":
                critical_alerts.append({
                    "type": alert_type,
                    "alert": alert
                })
    
    # 按时间排序，取最新的10条
    critical_alerts = sorted(critical_alerts, 
                           key=lambda x: x["alert"].get("deadline", x["alert"].get("last_update", "")),
                           reverse=True)[:10]
    
    return {
        "key_metrics": key_metrics,
        "alert_summary": summary,
        "critical_alerts": critical_alerts,
        "alert_trends": {
            "overdue_trend": "increasing",  # 这里可以添加趋势分析逻辑
            "workload_trend": "stable",
            "quality_trend": "improving"
        }
    }