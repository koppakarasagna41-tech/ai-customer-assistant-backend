from enum import StrEnum


class UserRole(StrEnum):
    CUSTOMER = "customer"
    SUPPORT_AGENT = "support_agent"
    SUPPORT_ADMIN = "support_admin"
    SUPERVISOR = "supervisor"
    SYSTEM_ADMIN = "system_admin"
