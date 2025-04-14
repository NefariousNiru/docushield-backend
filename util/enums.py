from enum import Enum

class Environment(Enum):
    PROD = "PROD"
    DEV = "DEV"

class AccountType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"