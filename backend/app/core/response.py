from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200
) -> Dict[str, Any]:
    """成功响应格式"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "success": True
    }


def error_response(
    message: str = "操作失败",
    code: int = 400,
    data: Any = None
) -> Dict[str, Any]:
    """错误响应格式"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "success": False
    }


def paginated_response(
    items: list,
    total: int,
    page: int,
    size: int,
    message: str = "查询成功"
) -> Dict[str, Any]:
    """分页响应格式"""
    return {
        "code": 200,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size if size > 0 else 0
        },
        "success": True
    }