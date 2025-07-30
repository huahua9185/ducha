from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.workflow import WorkflowStatus, NodeStatus
from app.services.workflow_service import get_workflow_service
from app.schemas.workflow import (
    WorkflowTemplateCreate, WorkflowTemplateUpdate, WorkflowTemplateResponse, WorkflowTemplateListResponse,
    WorkflowInstanceCreate, WorkflowInstanceUpdate, WorkflowInstanceResponse, WorkflowInstanceListResponse,
    WorkflowNodeResponse, WorkflowNodeListResponse,
    TaskCompleteRequest, TaskListQuery,
    WorkflowStats, UserTaskStats
)
from app.core.response import success_response, error_response

router = APIRouter()


# ========== 工作流模板管理 ==========

@router.post("/templates", response_model=WorkflowTemplateResponse, summary="创建工作流模板")
async def create_workflow_template(
    template_data: WorkflowTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建工作流模板"""
    try:
        workflow_service = get_workflow_service(db)
        
        # 检查模板代码是否已存在
        existing_template = workflow_service.get_template_by_code(template_data.code)
        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模板代码已存在"
            )
        
        template = workflow_service.create_template(template_data, str(current_user.id))
        return success_response(data=template)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/templates", response_model=WorkflowTemplateListResponse, summary="获取工作流模板列表")
async def get_workflow_templates(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    type_filter: Optional[str] = Query(None, description="模板类型筛选"),
    is_enabled: Optional[bool] = Query(None, description="是否启用筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作流模板列表"""
    try:
        workflow_service = get_workflow_service(db)
        skip = (page - 1) * size
        
        templates, total = workflow_service.get_template_list(
            skip=skip,
            limit=size,
            keyword=keyword,
            type_filter=type_filter,
            is_enabled=is_enabled
        )
        
        return success_response(data={
            "items": templates,
            "total": total,
            "page": page,
            "size": size,
            "pages": math.ceil(total / size)
        })
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/templates/{template_id}", response_model=WorkflowTemplateResponse, summary="获取工作流模板详情")
async def get_workflow_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作流模板详情"""
    try:
        workflow_service = get_workflow_service(db)
        template = workflow_service.get_template_by_id(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流模板不存在"
            )
        
        return success_response(data=template)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/instances", response_model=WorkflowInstanceListResponse, summary="获取工作流实例列表")
async def get_workflow_instances(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    status_filter: Optional[WorkflowStatus] = Query(None, description="状态筛选"),
    template_id: Optional[str] = Query(None, description="模板ID筛选"),
    business_type: Optional[str] = Query(None, description="业务类型筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作流实例列表"""
    try:
        workflow_service = get_workflow_service(db)
        skip = (page - 1) * size
        
        instances, total = workflow_service.get_instance_list(
            skip=skip,
            limit=size,
            keyword=keyword,
            status_filter=status_filter,
            template_id=template_id,
            business_type=business_type
        )
        
        return success_response(data={
            "items": instances,
            "total": total,
            "page": page,
            "size": size,
            "pages": math.ceil(total / size)
        })
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/my-tasks", response_model=WorkflowNodeListResponse, summary="获取我的待办任务")
async def get_my_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status_filter: Optional[NodeStatus] = Query(None, description="任务状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的待办任务"""
    try:
        workflow_service = get_workflow_service(db)
        skip = (page - 1) * size
        
        tasks, total = workflow_service.get_user_tasks(
            user_id=str(current_user.id),
            skip=skip,
            limit=size,
            status_filter=status_filter
        )
        
        return success_response(data={
            "items": tasks,
            "total": total,
            "page": page,
            "size": size,
            "pages": math.ceil(total / size)
        })
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/tasks/{task_id}/complete", summary="完成任务")
async def complete_task(
    task_id: str,
    request: TaskCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """完成任务"""
    try:
        workflow_service = get_workflow_service(db)
        success = workflow_service.complete_task(
            task_id=task_id,
            user_id=str(current_user.id),
            form_data=request.form_data,
            comment=request.comment
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        return success_response(message="任务完成成功")
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats", response_model=WorkflowStats, summary="获取工作流统计信息")
async def get_workflow_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作流统计信息"""
    try:
        # 这里应该实现统计查询逻辑
        # 暂时返回示例数据
        stats = WorkflowStats(
            total_templates=10,
            active_templates=8,
            total_instances=56,
            running_instances=12,
            completed_instances=40,
            pending_tasks=8,
            overdue_tasks=2
        )
        
        return success_response(data=stats)
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))