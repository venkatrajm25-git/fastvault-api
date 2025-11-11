from pydantic import BaseModel


class UpdateRole(BaseModel):
    role_id: int
    rolename: str
    status: int
