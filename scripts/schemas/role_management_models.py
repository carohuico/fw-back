from pydantic import BaseModel
from typing import Optional, List


class UserDetails(BaseModel):
    roleName: str
    accessTo: List[dict]


class RoleDetails(BaseModel):
    id: str
    roleName: str
    accessTo: List[dict]
