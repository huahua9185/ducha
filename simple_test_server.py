#!/usr/bin/env python3
"""
简化测试服务器
用于测试API连通性
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import json

# FastAPI应用
app = FastAPI(
    title="政府效能督查系统 - 测试服务器",
    description="用于测试前后端连通性的简化服务器",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 响应模型
class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None

# 模拟数据
MOCK_USERS = [
    {"id": 1, "username": "admin", "real_name": "系统管理员", "email": "admin@test.com"},
    {"id": 2, "username": "test_admin", "real_name": "测试管理员", "email": "test@test.com"},
]

MOCK_SUPERVISION_ITEMS = [
    {
        "id": 1,
        "number": "DB20250001",
        "title": "推进重大项目建设进度",
        "content": "督办各部门重大项目建设进度，确保按时完成年度目标任务。",
        "type": "key",
        "urgency": "high",
        "status": "in_progress",
        "creator_id": 1,
        "deadline": "2025-08-30T23:59:59",
        "completion_rate": 60
    },
    {
        "id": 2,
        "number": "DB20250002", 
        "title": "优化营商环境专项行动",
        "content": "深化'放管服'改革，优化营商环境，提升政务服务效率。",
        "type": "special",
        "urgency": "medium",
        "status": "pending",
        "creator_id": 1,
        "deadline": "2025-09-15T23:59:59",
        "completion_rate": 0
    }
]

MOCK_WORKFLOWS = [
    {
        "id": 1,
        "name": "督办事项审批流程",
        "code": "SUPERVISION_APPROVAL",
        "description": "督办事项从创建到完成的标准审批流程",
        "is_enabled": True
    }
]

MOCK_TASKS = [
    {
        "id": 1,
        "title": "审核重大项目建设进度报告",
        "description": "审核各部门提交的重大项目建设进度报告",
        "status": "pending",
        "assignee_id": 1,
        "due_date": "2025-08-25T23:59:59"
    }
]

# 健康检查
@app.get("/health")
@app.get("/api/v1/health")  
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": {"status": "healthy", "message": "模拟数据库连接正常"},
            "redis": {"status": "not_configured", "message": "Redis未配置"}
        }
    }

@app.get("/ping")
@app.get("/api/v1/ping")
async def ping():
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }

# 认证相关
@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")
    
    # 模拟登录验证
    if username in ["admin", "test_admin"] and password in ["admin123456", "test123456"]:
        return ApiResponse(
            data={
                "access_token": "mock_access_token_123456",
                "token_type": "bearer",
                "expires_in": 7200,
                "user": next(u for u in MOCK_USERS if u["username"] == username)
            }
        ).dict()
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

@app.post("/api/v1/auth/register")
async def register(user_data: dict):
    return ApiResponse(
        data={"message": "用户注册成功", "user_id": 3}
    ).dict()

# 用户管理
@app.get("/api/v1/users/me")
async def get_current_user():
    return ApiResponse(data=MOCK_USERS[0]).dict()

@app.get("/api/v1/users")
async def get_users(page: int = 1, size: int = 10):
    return ApiResponse(
        data={
            "items": MOCK_USERS,
            "total": len(MOCK_USERS),
            "page": page,
            "size": size,
            "pages": 1
        }
    ).dict()

# 督办事项管理
@app.get("/api/v1/supervision")
async def get_supervision_list(page: int = 1, size: int = 10):
    return ApiResponse(
        data={
            "items": MOCK_SUPERVISION_ITEMS,
            "total": len(MOCK_SUPERVISION_ITEMS),
            "page": page,
            "size": size,
            "pages": 1
        }
    ).dict()

@app.post("/api/v1/supervision")
async def create_supervision(item_data: dict):
    new_item = {
        "id": len(MOCK_SUPERVISION_ITEMS) + 1,
        "number": f"DB2025{len(MOCK_SUPERVISION_ITEMS) + 1:04d}",
        **item_data
    }
    MOCK_SUPERVISION_ITEMS.append(new_item)
    return ApiResponse(data=new_item).dict()

@app.get("/api/v1/supervision/{item_id}")
async def get_supervision_detail(item_id: int):
    item = next((item for item in MOCK_SUPERVISION_ITEMS if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="督办事项不存在")
    return ApiResponse(data=item).dict()

# 工作流管理
@app.get("/api/v1/workflow/templates")
async def get_workflow_templates(page: int = 1, size: int = 10):
    return ApiResponse(
        data={
            "items": MOCK_WORKFLOWS,
            "total": len(MOCK_WORKFLOWS),
            "page": page,
            "size": size,
            "pages": 1
        }
    ).dict()

@app.get("/api/v1/workflow/instances")
async def get_workflow_instances(page: int = 1, size: int = 10):
    return ApiResponse(
        data={
            "items": [],
            "total": 0,
            "page": page,
            "size": size,
            "pages": 0
        }
    ).dict()

@app.get("/api/v1/workflow/my-tasks")
async def get_my_tasks(page: int = 1, size: int = 10):
    return ApiResponse(
        data={
            "items": MOCK_TASKS,
            "total": len(MOCK_TASKS),
            "page": page,
            "size": size,
            "pages": 1
        }
    ).dict()

# 监控预警
@app.get("/api/v1/monitoring/stats")
async def get_monitoring_stats():
    return ApiResponse(
        data={
            "total_items": 15,
            "in_progress": 8,
            "overdue": 2,
            "completed": 5,
            "alert_count": 3,
            "high_priority": 4
        }
    ).dict()

@app.get("/api/v1/monitoring/alerts")
async def get_alerts(page: int = 1, size: int = 10):
    alerts = [
        {
            "id": 1,
            "type": "overdue",
            "title": "重大项目建设进度督办即将超期",
            "level": "warning",
            "created_at": "2025-07-29T10:00:00"
        },
        {
            "id": 2,
            "type": "slow_progress",
            "title": "营商环境专项行动进度缓慢",
            "level": "attention",
            "created_at": "2025-07-29T14:30:00"
        }
    ]
    return ApiResponse(
        data={
            "items": alerts,
            "total": len(alerts),
            "page": page,
            "size": size,
            "pages": 1
        }
    ).dict()

# 统计分析
@app.get("/api/v1/analytics/overview")
async def get_analytics_overview(start_date: str = None, end_date: str = None):
    return ApiResponse(
        data={
            "total_supervision": 15,
            "completed_rate": 0.67,
            "average_completion_time": 12.5,
            "department_stats": [
                {"name": "发改委", "total": 5, "completed": 3},
                {"name": "财政局", "total": 4, "completed": 3},
                {"name": "人社局", "total": 3, "completed": 2}
            ],
            "monthly_trends": [
                {"month": "2025-01", "created": 5, "completed": 4},
                {"month": "2025-02", "created": 4, "completed": 3},
                {"month": "2025-03", "created": 6, "completed": 5}
            ]
        }
    ).dict()

if __name__ == "__main__":
    print("启动测试服务器...")
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )