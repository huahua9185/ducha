from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    users,
    roles,
    departments,
    supervision,
    workflow,
    notifications,
    files,
    analytics,
    system,
    monitoring,
    health
)

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户管理路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(departments.router, prefix="/departments", tags=["部门管理"])

# 督办管理路由
api_router.include_router(supervision.router, prefix="/supervision", tags=["督办管理"])

# 工作流路由
api_router.include_router(workflow.router, prefix="/workflow", tags=["工作流"])

# 通知路由
api_router.include_router(notifications.router, prefix="/notifications", tags=["消息通知"])

# 文件管理路由
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])

# 统计分析路由
api_router.include_router(analytics.router, prefix="/analytics", tags=["统计分析"])

# 系统管理路由
api_router.include_router(system.router, prefix="/system", tags=["系统管理"])

# 监控预警路由
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["监控预警"])

# 健康检查路由
api_router.include_router(health.router, tags=["健康检查"])