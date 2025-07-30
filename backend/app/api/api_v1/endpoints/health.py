from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
from datetime import datetime
import platform
import psutil

from app.api.deps import get_db
from app.core.config import settings
from app.core.response import success_response

router = APIRouter()

@router.get("/health", summary="系统健康检查")
async def health_check(db: Session = Depends(get_db)):
    """
    系统健康检查端点
    检查数据库连接、Redis连接等系统状态
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {}
    }
    
    # 检查数据库连接
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = {
            "status": "healthy",
            "message": "数据库连接正常"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "message": f"数据库连接失败: {str(e)}"
        }
    
    # 检查Redis连接（如果配置了Redis）
    try:
        if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status["services"]["redis"] = {
                "status": "healthy",
                "message": "Redis连接正常"
            }
        else:
            health_status["services"]["redis"] = {
                "status": "not_configured",
                "message": "Redis未配置"
            }
    except Exception as e:
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis连接失败: {str(e)}"
        }
    
    # 系统信息
    try:
        health_status["system"] = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    except Exception as e:
        health_status["system"] = {
            "error": f"获取系统信息失败: {str(e)}"
        }
    
    return success_response(data=health_status)

@router.get("/ping", summary="简单连通性检查")
async def ping():
    """简单的ping检查"""
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }