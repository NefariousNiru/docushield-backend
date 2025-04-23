from enum import Enum

class Environment(Enum):
    PROD = "PROD"
    DEV = "DEV"

class AccountType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"

class AuditAction(Enum):
    REQUESTED_DOCUMENT = "Requested Document"
    MODIFIED_REQUEST = "Modified Request" # Represents a general modification in access status made by the User
    DOWNLOADED_DOCUMENT = "Downloaded Document"
    ADDED_DOCUMENT = "Added Document"
    SIGNIN = "SignIn"
    SIGNUP = "SignUp"
    LOGOUT = "Logout"

class AccessStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    COMPLETED = "COMPLETED"