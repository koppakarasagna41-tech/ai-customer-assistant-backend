from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    SUPPORT_AGENT = "support_agent"
    SUPPORT_ADMIN = "support_admin"
    SUPERVISOR = "supervisor"
    SYSTEM_ADMIN = "system_admin"
