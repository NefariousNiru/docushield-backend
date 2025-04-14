from pydantic import BaseModel
from model.sign_in_request import SignInRequest
from util.enums import AccountType


class SignUpRequest(SignInRequest):
    name: str
    account_type: AccountType

