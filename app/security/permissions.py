from enum import Enum
from typing import List, Dict
from app.security.roles import UserRole

class Permission(str, Enum):
    CREATE_TICKET = "create_ticket"
    UPDATE_TICKET = "update_ticket"
    DELETE_TICKET = "delete_ticket"
    ASSIGN_TICKET = "assign_ticket"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_REPORTS = "export_reports"
    ACCESS_AI_CHAT = "access_ai_chat"
    MANAGE_KNOWLEDGE_BASE = "manage_knowledge_base"
    MANAGE_USERS = "manage_users"

# Define default permissions for each role
ROLE_PERMISSIONS: Dict[str, List[Permission]] = {
    UserRole.CUSTOMER.value: [
        Permission.CREATE_TICKET,
        Permission.UPDATE_TICKET,
        Permission.ACCESS_AI_CHAT,
    ],
    UserRole.SUPPORT_AGENT.value: [
        Permission.CREATE_TICKET,
        Permission.UPDATE_TICKET,
        Permission.ASSIGN_TICKET,
        Permission.ACCESS_AI_CHAT,
    ],
    UserRole.SUPPORT_ADMIN.value: [
        Permission.CREATE_TICKET,
        Permission.UPDATE_TICKET,
        Permission.ASSIGN_TICKET,
        Permission.ACCESS_AI_CHAT,
        Permission.MANAGE_KNOWLEDGE_BASE,
    ],
    UserRole.SUPERVISOR.value: [
        Permission.CREATE_TICKET,
        Permission.UPDATE_TICKET,
        Permission.ASSIGN_TICKET,
        Permission.ACCESS_AI_CHAT,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_REPORTS,
        Permission.MANAGE_KNOWLEDGE_BASE,
    ],
    UserRole.SYSTEM_ADMIN.value: [
        Permission.CREATE_TICKET,
        Permission.UPDATE_TICKET,
        Permission.DELETE_TICKET,
        Permission.ASSIGN_TICKET,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_REPORTS,
        Permission.ACCESS_AI_CHAT,
        Permission.MANAGE_KNOWLEDGE_BASE,
        Permission.MANAGE_USERS,
    ],
}
