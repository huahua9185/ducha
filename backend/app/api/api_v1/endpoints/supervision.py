from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.supervision import (
    SupervisionItem, SupervisionItemCreate, SupervisionItemUpdate, 
    SupervisionItemDetail, SupervisionItemList,
    TaskAssignment, TaskAssignmentCreate, TaskAssignmentUpdate,
    ProgressReport, ProgressReportCreate, ProgressReportUpdate,
    StatusLog, SupervisionEvaluationCreate,
    SupervisionType, SupervisionStatus, SupervisionUrgency,
    SupervisionStats
)
from app.services import supervision_service

router = APIRouter()


# 督办事项管理
@router.get("/", response_model=SupervisionItemList)
def read_supervision_items(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    search: str = Query(None, description="搜索关键词"),
    type: SupervisionType = Query(None, description="督办类型"),
    status: SupervisionStatus = Query(None, description="督办状态"),
    urgency: SupervisionUrgency = Query(None, description="紧急程度"),
    creator_id: UUID = Query(None, description="创建人ID"),
    responsible_department_id: UUID = Query(None, description="责任部门ID"),
    is_key: bool = Query(None, description="是否重点督办"),
    start_date_from: datetime = Query(None, description="开始时间起"),
    start_date_to: datetime = Query(None, description="开始时间止"),
    deadline_from: datetime = Query(None, description="截止时间起"),
    deadline_to: datetime = Query(None, description="截止时间止"),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取督办事项列表"""
    items = supervision_service.get_supervision_items(
        db=db, skip=skip, limit=limit, search=search,
        type=type, status=status, urgency=urgency,
        creator_id=creator_id, responsible_department_id=responsible_department_id,
        is_key=is_key, start_date_from=start_date_from, start_date_to=start_date_to,
        deadline_from=deadline_from, deadline_to=deadline_to
    )
    
    total = supervision_service.count_supervision_items(
        db=db, search=search, type=type, status=status, urgency=urgency,
        creator_id=creator_id, responsible_department_id=responsible_department_id,
        is_key=is_key, start_date_from=start_date_from, start_date_to=start_date_to,
        deadline_from=deadline_from, deadline_to=deadline_to
    )
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/", response_model=SupervisionItem)
def create_supervision_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: SupervisionItemCreate,
    current_user: User = Depends(deps.require_supervision_create)
) -> Any:
    """创建督办事项"""
    item = supervision_service.create_supervision_item(
        db=db, item_create=item_in, creator_id=current_user.id
    )
    return item


@router.get("/{item_id}", response_model=SupervisionItemDetail)
def read_supervision_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取督办事项详情"""
    item = supervision_service.get_supervision_item(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="督办事项不存在"
        )
    return item


@router.put("/{item_id}", response_model=SupervisionItem)
def update_supervision_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    item_in: SupervisionItemUpdate,
    current_user: User = Depends(deps.require_supervision_update)
) -> Any:
    """更新督办事项"""
    item = supervision_service.update_supervision_item(
        db=db, item_id=item_id, item_update=item_in, operator_id=current_user.id
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="督办事项不存在"
        )
    return item


@router.delete("/{item_id}")
def delete_supervision_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    current_user: User = Depends(deps.require_supervision_delete)
) -> Any:
    """删除督办事项"""
    success = supervision_service.delete_supervision_item(
        db=db, item_id=item_id, operator_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="督办事项不存在"
        )
    return {"message": "督办事项删除成功"}


@router.post("/{item_id}/status")
def change_supervision_status(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    new_status: SupervisionStatus,
    reason: str = None,
    current_user: User = Depends(deps.require_supervision_update)
) -> Any:
    """更改督办状态"""
    item = supervision_service.change_supervision_status(
        db=db, item_id=item_id, new_status=new_status,
        operator_id=current_user.id, reason=reason
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="督办事项不存在"
        )
    return {"message": "状态更新成功", "item": item}


@router.post("/{item_id}/evaluate")
def evaluate_supervision_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    evaluation: SupervisionEvaluationCreate,
    current_user: User = Depends(deps.require_supervision_update)
) -> Any:
    """评价督办事项"""
    item = supervision_service.evaluate_supervision_item(
        db=db, item_id=item_id, evaluation=evaluation, evaluator_id=current_user.id
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="督办事项不存在"
        )
    return {"message": "评价提交成功", "item": item}


# 任务分配管理
@router.get("/{item_id}/tasks", response_model=List[TaskAssignment])
def read_task_assignments(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取督办事项的任务分配列表"""
    tasks = supervision_service.get_task_assignments_by_supervision(db, item_id)
    return tasks


@router.post("/{item_id}/tasks", response_model=TaskAssignment)
def create_task_assignment(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    task_in: TaskAssignmentCreate,
    current_user: User = Depends(deps.require_supervision_update)
) -> Any:
    """创建任务分配"""
    # 验证督办事项存在
    item = supervision_service.get_supervision_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="督办事项不存在"
        )
    
    task_in.supervision_item_id = item_id
    task = supervision_service.create_task_assignment(
        db=db, task_create=task_in, assigner_id=current_user.id
    )
    return task


@router.put("/tasks/{task_id}", response_model=TaskAssignment)
def update_task_assignment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: UUID,
    task_in: TaskAssignmentUpdate,
    current_user: User = Depends(deps.require_supervision_update)
) -> Any:
    """更新任务分配"""
    task = supervision_service.update_task_assignment(
        db=db, task_id=task_id, task_update=task_in, operator_id=current_user.id
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务分配不存在"
        )
    return task


@router.post("/tasks/{task_id}/accept")
def accept_task_assignment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """接收任务分配"""
    task = supervision_service.accept_task_assignment(
        db=db, task_id=task_id, assignee_id=current_user.id
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在或您无权接收此任务"
        )
    return {"message": "任务接收成功", "task": task}


@router.post("/tasks/{task_id}/complete")
def complete_task_assignment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: UUID,
    actual_hours: float = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """完成任务分配"""
    task = supervision_service.complete_task_assignment(
        db=db, task_id=task_id, assignee_id=current_user.id, actual_hours=actual_hours
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在或您无权完成此任务"
        )
    return {"message": "任务完成成功", "task": task}


# 进度报告管理
@router.get("/{item_id}/reports", response_model=List[ProgressReport])
def read_progress_reports(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取督办事项的进度报告列表"""
    reports = supervision_service.get_progress_reports_by_supervision(
        db, item_id, skip=skip, limit=limit
    )
    return reports


@router.post("/{item_id}/reports", response_model=ProgressReport)
def create_progress_report(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    report_in: ProgressReportCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """创建进度报告"""
    # 验证督办事项存在
    item = supervision_service.get_supervision_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="督办事项不存在"
        )
    
    report_in.supervision_item_id = item_id
    report = supervision_service.create_progress_report(
        db=db, report_create=report_in, reporter_id=current_user.id
    )
    return report


@router.put("/reports/{report_id}", response_model=ProgressReport)
def update_progress_report(
    *,
    db: Session = Depends(deps.get_db),
    report_id: UUID,
    report_in: ProgressReportUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """更新进度报告"""
    report = supervision_service.update_progress_report(
        db=db, report_id=report_id, report_update=report_in, operator_id=current_user.id
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="进度报告不存在"
        )
    return report


# 状态日志
@router.get("/{item_id}/logs", response_model=List[StatusLog])
def read_status_logs(
    *,
    db: Session = Depends(deps.get_db),
    item_id: UUID,
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取督办事项的状态变更日志"""
    logs = supervision_service.get_status_logs_by_supervision(db, item_id)
    return logs


# 统计分析
@router.get("/stats/overview", response_model=SupervisionStats)
def get_supervision_stats(
    *,
    db: Session = Depends(deps.get_db),
    department_id: UUID = Query(None, description="部门ID"),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取督办统计概览"""
    stats = supervision_service.get_supervision_stats(db, department_id)
    return stats


@router.get("/stats/departments")
def get_department_stats(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取各部门统计数据"""
    stats = supervision_service.get_department_stats(db)
    return {"data": stats}


@router.get("/overdue", response_model=List[SupervisionItem])
def get_overdue_items(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取逾期督办事项"""
    items = supervision_service.get_overdue_items(db, limit=limit)
    return items


@router.get("/urgent", response_model=List[SupervisionItem])
def get_urgent_items(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(deps.require_supervision_read)
) -> Any:
    """获取紧急督办事项"""
    items = supervision_service.get_urgent_items(db, limit=limit)
    return items