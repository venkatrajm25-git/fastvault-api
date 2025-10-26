from pydantic import BaseModel
from typing import Optional


class RegisterUserBaseModel(BaseModel):
    email: str
    password: str
    username: str
    status: int
    role: int


class LoginUserBaseModel(BaseModel):
    email: str
    password: str
