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


class UpdateUserRequest(BaseModel):
    id: int
    username: str
    status: int
    role: int


class ResetPassBaseModel(BaseModel):
    token: str
    newPassword: str
    confirmPassword: str
