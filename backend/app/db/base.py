# 导入所有的模型，这样 Alembic 可以自动发现它们
from app.models.base import Base
from app.models.user import User, Role, Permission, UserRole
from app.models.organization import Organization, Department
from app.models.supervision import SupervisionItem, TaskAssignment, ProgressReport, StatusLog
from app.models.workflow import WorkflowTemplate, WorkflowInstance, WorkflowNode, WorkflowTransition
from app.models.notification import Notification, NotificationTemplate, NotificationRule
from app.models.attachment import Attachment, AttachmentPermission
from app.models.system import SystemConfig, OperationLog, SystemSetting, DataDictionary