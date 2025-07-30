from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from enum import Enum

from app.models.supervision import SupervisionItem, TaskAssignment, SupervisionStatus, TaskStatus, SupervisionUrgency
from app.models.user import User
from app.models.notification import Notification, NotificationType, NotificationChannel
from app.services.supervision_service import create_status_log
from app.services.notification_service import create_notification


class AlertLevel(str, Enum):
    """预警级别"""
    NORMAL = "normal"      # 正常
    ATTENTION = "attention" # 关注
    WARNING = "warning"    # 预警
    CRITICAL = "critical"  # 紧急


class RiskType(str, Enum):
    """风险类型"""
    OVERDUE = "overdue"           # 逾期风险
    DELAY = "delay"               # 延期风险
    QUALITY = "quality"           # 质量风险
    RESOURCE = "resource"         # 资源风险
    COMMUNICATION = "communication" # 沟通风险


def check_overdue_items(db: Session) -> List[Dict[str, Any]]:
    """检查逾期督办事项"""
    now = datetime.utcnow()
    
    overdue_items = db.query(SupervisionItem).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.status.in_([SupervisionStatus.PENDING, SupervisionStatus.IN_PROGRESS]),
        SupervisionItem.deadline < now
    ).all()
    
    alerts = []
    for item in overdue_items:
        # 计算逾期天数
        overdue_days = (now - item.deadline).days
        
        # 确定预警级别
        if overdue_days <= 1:
            level = AlertLevel.WARNING
        elif overdue_days <= 3:
            level = AlertLevel.CRITICAL
        else:
            level = AlertLevel.CRITICAL
        
        alerts.append({
            "id": item.id,
            "title": item.title,
            "number": item.number,
            "level": level,
            "type": RiskType.OVERDUE,
            "message": f"督办事项已逾期 {overdue_days} 天",
            "deadline": item.deadline,
            "overdue_days": overdue_days,
            "responsible_department_id": item.responsible_department_id,
            "creator_id": item.creator_id,
            "urgency": item.urgency
        })
    
    return alerts


def check_upcoming_deadlines(db: Session, days_ahead: int = 3) -> List[Dict[str, Any]]:
    """检查即将到期的督办事项"""
    now = datetime.utcnow()
    deadline_threshold = now + timedelta(days=days_ahead)
    
    upcoming_items = db.query(SupervisionItem).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.status.in_([SupervisionStatus.PENDING, SupervisionStatus.IN_PROGRESS]),
        SupervisionItem.deadline.between(now, deadline_threshold)
    ).all()
    
    alerts = []
    for item in upcoming_items:
        # 计算剩余天数
        remaining_days = (item.deadline - now).days
        
        # 确定预警级别
        if remaining_days >= 2:
            level = AlertLevel.ATTENTION
        elif remaining_days >= 1:
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.CRITICAL
        
        alerts.append({
            "id": item.id,
            "title": item.title,
            "number": item.number,
            "level": level,
            "type": RiskType.DELAY,
            "message": f"督办事项将在 {remaining_days} 天后到期",
            "deadline": item.deadline,
            "remaining_days": remaining_days,
            "responsible_department_id": item.responsible_department_id,
            "creator_id": item.creator_id,
            "urgency": item.urgency
        })
    
    return alerts


def check_slow_progress_items(db: Session) -> List[Dict[str, Any]]:
    """检查进度缓慢的督办事项"""
    now = datetime.utcnow()
    
    # 查找进行中且进度低于预期的督办事项
    slow_items = db.query(SupervisionItem).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.status == SupervisionStatus.IN_PROGRESS
    ).all()
    
    alerts = []
    for item in slow_items:
        # 计算预期进度
        total_duration = (item.deadline - item.start_date).total_seconds()
        elapsed_duration = (now - item.start_date).total_seconds()
        expected_progress = min(100, int((elapsed_duration / total_duration) * 100))
        
        # 如果实际进度低于预期进度的70%，则发出预警
        if item.completion_rate < expected_progress * 0.7:
            progress_gap = expected_progress - item.completion_rate
            
            # 确定预警级别
            if progress_gap <= 20:
                level = AlertLevel.ATTENTION
            elif progress_gap <= 40:
                level = AlertLevel.WARNING
            else:
                level = AlertLevel.CRITICAL
            
            alerts.append({
                "id": item.id,
                "title": item.title,
                "number": item.number,
                "level": level,
                "type": RiskType.DELAY,
                "message": f"督办进度缓慢，实际进度 {item.completion_rate}%，预期进度 {expected_progress}%",
                "actual_progress": item.completion_rate,
                "expected_progress": expected_progress,
                "progress_gap": progress_gap,
                "responsible_department_id": item.responsible_department_id,
                "creator_id": item.creator_id
            })
    
    return alerts


def check_task_overdue(db: Session) -> List[Dict[str, Any]]:
    """检查逾期任务"""
    now = datetime.utcnow()
    
    overdue_tasks = db.query(TaskAssignment).filter(
        TaskAssignment.is_deleted == False,
        TaskAssignment.status.in_([TaskStatus.ASSIGNED, TaskStatus.ACCEPTED, TaskStatus.IN_PROGRESS]),
        TaskAssignment.deadline < now
    ).all()
    
    alerts = []
    for task in overdue_tasks:
        overdue_days = (now - task.deadline).days
        
        # 确定预警级别
        if overdue_days <= 1:
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.CRITICAL
        
        alerts.append({
            "id": task.id,
            "title": task.title,
            "supervision_item_id": task.supervision_item_id,
            "level": level,
            "type": RiskType.OVERDUE,
            "message": f"任务已逾期 {overdue_days} 天",
            "deadline": task.deadline,
            "overdue_days": overdue_days,
            "assignee_id": task.assignee_id,
            "assigned_department_id": task.assigned_department_id
        })
    
    return alerts


def check_high_workload_users(db: Session) -> List[Dict[str, Any]]:
    """检查工作负荷过高的用户"""
    # 查询每个用户的活跃任务数量
    active_task_counts = db.query(
        TaskAssignment.assignee_id,
        func.count(TaskAssignment.id).label('task_count')
    ).filter(
        TaskAssignment.is_deleted == False,
        TaskAssignment.status.in_([TaskStatus.ASSIGNED, TaskStatus.ACCEPTED, TaskStatus.IN_PROGRESS])
    ).group_by(TaskAssignment.assignee_id).all()
    
    alerts = []
    for user_id, task_count in active_task_counts:
        # 如果活跃任务超过10个，发出预警
        if task_count >= 10:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # 确定预警级别
                if task_count >= 20:
                    level = AlertLevel.CRITICAL
                elif task_count >= 15:
                    level = AlertLevel.WARNING
                else:
                    level = AlertLevel.ATTENTION
                
                alerts.append({
                    "user_id": user_id,
                    "user_name": user.real_name,
                    "level": level,
                    "type": RiskType.RESOURCE,
                    "message": f"用户 {user.real_name} 当前有 {task_count} 个活跃任务，工作负荷较高",
                    "task_count": task_count,
                    "department_id": user.department_id
                })
    
    return alerts


def check_urgent_items_without_progress(db: Session, hours_threshold: int = 24) -> List[Dict[str, Any]]:
    """检查紧急督办事项无进展情况"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_threshold)
    
    # 查找紧急督办事项且长时间无进展
    urgent_items = db.query(SupervisionItem).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.urgency == SupervisionUrgency.HIGH,
        SupervisionItem.status.in_([SupervisionStatus.PENDING, SupervisionStatus.IN_PROGRESS]),
        SupervisionItem.updated_at < cutoff_time
    ).all()
    
    alerts = []
    for item in urgent_items:
        hours_no_update = int((datetime.utcnow() - item.updated_at).total_seconds() / 3600)
        
        alerts.append({
            "id": item.id,
            "title": item.title,
            "number": item.number,
            "level": AlertLevel.CRITICAL,
            "type": RiskType.COMMUNICATION,
            "message": f"紧急督办事项已 {hours_no_update} 小时无进展更新",
            "hours_no_update": hours_no_update,
            "last_update": item.updated_at,
            "responsible_department_id": item.responsible_department_id,
            "creator_id": item.creator_id
        })
    
    return alerts


def check_quality_risks(db: Session) -> List[Dict[str, Any]]:
    """检查质量风险"""
    # 查找返工次数较多的督办事项（通过状态变更日志判断）
    from app.models.supervision import StatusLog
    
    # 统计每个督办事项的状态变更次数
    status_change_counts = db.query(
        StatusLog.supervision_item_id,
        func.count(StatusLog.id).label('change_count')
    ).filter(
        StatusLog.is_deleted == False,
        StatusLog.action_type == 'status_change'
    ).group_by(StatusLog.supervision_item_id).having(
        func.count(StatusLog.id) >= 5  # 状态变更超过5次
    ).all()
    
    alerts = []
    for item_id, change_count in status_change_counts:
        item = db.query(SupervisionItem).filter(SupervisionItem.id == item_id).first()
        if item and not item.is_deleted:
            alerts.append({
                "id": item.id,
                "title": item.title,
                "number": item.number,
                "level": AlertLevel.WARNING,
                "type": RiskType.QUALITY,
                "message": f"督办事项状态变更频繁（{change_count}次），可能存在质量问题",
                "change_count": change_count,
                "responsible_department_id": item.responsible_department_id,
                "creator_id": item.creator_id
            })
    
    return alerts


def get_comprehensive_alerts(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """获取综合预警信息"""
    alerts = {
        "overdue_items": check_overdue_items(db),
        "upcoming_deadlines": check_upcoming_deadlines(db),
        "slow_progress": check_slow_progress_items(db),
        "overdue_tasks": check_task_overdue(db),
        "high_workload_users": check_high_workload_users(db),
        "urgent_no_progress": check_urgent_items_without_progress(db),
        "quality_risks": check_quality_risks(db)
    }
    
    return alerts


def get_alert_summary(alerts: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """获取预警摘要"""
    total_alerts = sum(len(alert_list) for alert_list in alerts.values())
    critical_count = 0
    warning_count = 0
    attention_count = 0
    
    for alert_list in alerts.values():
        for alert in alert_list:
            level = alert.get('level', AlertLevel.NORMAL)
            if level == AlertLevel.CRITICAL:
                critical_count += 1
            elif level == AlertLevel.WARNING:
                warning_count += 1
            elif level == AlertLevel.ATTENTION:
                attention_count += 1
    
    return {
        "total_alerts": total_alerts,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "attention_count": attention_count,
        "alert_distribution": {
            "overdue_items": len(alerts["overdue_items"]),
            "upcoming_deadlines": len(alerts["upcoming_deadlines"]),
            "slow_progress": len(alerts["slow_progress"]),
            "overdue_tasks": len(alerts["overdue_tasks"]),
            "high_workload_users": len(alerts["high_workload_users"]),
            "urgent_no_progress": len(alerts["urgent_no_progress"]),
            "quality_risks": len(alerts["quality_risks"])
        }
    }


def send_alert_notifications(db: Session, alerts: Dict[str, List[Dict[str, Any]]]):
    """发送预警通知"""
    # 处理逾期督办事项通知
    for alert in alerts["overdue_items"]:
        if alert["level"] in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
            # 通知责任部门和创建人
            create_notification(
                db=db,
                title="督办事项逾期预警",
                content=f"督办事项「{alert['title']}」已逾期{alert['overdue_days']}天，请及时处理。",
                type=NotificationType.WARNING,
                channels=[NotificationChannel.SYSTEM, NotificationChannel.EMAIL],
                recipient_id=alert["creator_id"],
                related_id=alert["id"],
                related_type="supervision_item"
            )
    
    # 处理即将到期的督办事项通知
    for alert in alerts["upcoming_deadlines"]:
        if alert["level"] == AlertLevel.CRITICAL:
            create_notification(
                db=db,
                title="督办事项即将到期",
                content=f"督办事项"{alert['title']}"将在{alert['remaining_days']}天后到期，请注意及时完成。",
                type=NotificationType.REMINDER,
                channels=[NotificationChannel.SYSTEM],
                recipient_id=alert["creator_id"],
                related_id=alert["id"],
                related_type="supervision_item"
            )
    
    # 处理进度缓慢的督办事项通知
    for alert in alerts["slow_progress"]:
        if alert["level"] in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
            create_notification(
                db=db,
                title="督办进度预警",
                content=f"督办事项"{alert['title']}"进度缓慢，实际进度{alert['actual_progress']}%，预期进度{alert['expected_progress']}%。",
                type=NotificationType.WARNING,
                channels=[NotificationChannel.SYSTEM],
                recipient_id=alert["creator_id"],
                related_id=alert["id"],
                related_type="supervision_item"
            )
    
    # 处理工作负荷过高的用户通知
    for alert in alerts["high_workload_users"]:
        if alert["level"] == AlertLevel.CRITICAL:
            create_notification(
                db=db,
                title="工作负荷预警",
                content=f"您当前有{alert['task_count']}个活跃任务，工作负荷较高，建议合理安排时间。",
                type=NotificationType.WARNING,
                channels=[NotificationChannel.SYSTEM],
                recipient_id=alert["user_id"],
                related_id=None,
                related_type="workload_warning"
            )


def schedule_monitoring_tasks(db: Session):
    """定时监控任务"""
    # 获取所有预警信息
    alerts = get_comprehensive_alerts(db)
    
    # 发送通知
    send_alert_notifications(db, alerts)
    
    # 更新逾期状态
    update_overdue_status(db)
    
    return alerts


def update_overdue_status(db: Session):
    """更新逾期状态"""
    now = datetime.utcnow()
    
    # 更新逾期的督办事项状态
    overdue_items = db.query(SupervisionItem).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.status.in_([SupervisionStatus.PENDING, SupervisionStatus.IN_PROGRESS]),
        SupervisionItem.deadline < now,
        SupervisionItem.status != SupervisionStatus.OVERDUE
    ).all()
    
    for item in overdue_items:
        old_status = item.status
        item.status = SupervisionStatus.OVERDUE
        item.updated_at = now
        
        # 创建状态变更日志
        create_status_log(
            db=db,
            supervision_item_id=item.id,
            operator_id=None,  # 系统自动更新
            action_type="auto_status_change",
            old_status=old_status.value,
            new_status=SupervisionStatus.OVERDUE.value,
            reason="系统自动检测逾期并更新状态"
        )
    
    db.commit()
    
    return len(overdue_items)


def get_department_risk_analysis(db: Session, department_id: UUID) -> Dict[str, Any]:
    """获取部门风险分析"""
    # 获取部门的督办事项
    department_items = db.query(SupervisionItem).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.responsible_department_id == department_id
    ).all()
    
    if not department_items:
        return {
            "department_id": department_id,
            "total_items": 0,
            "risk_score": 0,
            "risk_level": AlertLevel.NORMAL,
            "risk_factors": []
        }
    
    risk_score = 0
    risk_factors = []
    
    # 计算各种风险因素
    overdue_count = sum(1 for item in department_items if item.status == SupervisionStatus.OVERDUE)
    if overdue_count > 0:
        risk_score += overdue_count * 10
        risk_factors.append(f"有{overdue_count}个逾期督办事项")
    
    # 进度缓慢的督办事项
    slow_progress_count = sum(1 for item in department_items 
                            if item.status == SupervisionStatus.IN_PROGRESS and item.completion_rate < 30)
    if slow_progress_count > 0:
        risk_score += slow_progress_count * 5
        risk_factors.append(f"有{slow_progress_count}个进度缓慢的督办事项")
    
    # 紧急督办事项比例
    urgent_count = sum(1 for item in department_items if item.urgency == SupervisionUrgency.HIGH)
    urgent_ratio = urgent_count / len(department_items)
    if urgent_ratio > 0.3:
        risk_score += int(urgent_ratio * 20)
        risk_factors.append(f"紧急督办事项比例较高（{urgent_ratio:.1%}）")
    
    # 确定风险级别
    if risk_score >= 50:
        risk_level = AlertLevel.CRITICAL
    elif risk_score >= 25:
        risk_level = AlertLevel.WARNING
    elif risk_score >= 10:
        risk_level = AlertLevel.ATTENTION
    else:
        risk_level = AlertLevel.NORMAL
    
    return {
        "department_id": department_id,
        "total_items": len(department_items),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "overdue_count": overdue_count,
        "slow_progress_count": slow_progress_count,
        "urgent_count": urgent_count,
        "urgent_ratio": urgent_ratio
    }