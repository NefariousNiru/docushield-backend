from enum import Enum

class Environment(Enum):
    PROD = "PROD"
    DEV = "DEV"

class AccountType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"

class AuditAction(Enum):
    REQUESTED_DOCUMENT = "Requested Document"
    APPROVED_REQUEST = "Approved Request"
    DOWNLOADED_DOCUMENT = "Downloaded Document"
    REVOKED_ACCESS = "Revoked Access"
    LOGIN = "Login"
    LOGOUT = "Logout"

class AccessStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    COMPLETED = "COMPLETED"