from pydantic import BaseModel
from typing import Optional


class UserActions(BaseModel):
    user_id: str
    user_name: Optional[str]
    user_type: Optional[str]
    email: str
    password: str
    action: str


class UserDetails(BaseModel):
    fullName: str
    userName: str
    userRole: str


class DeleteUser(BaseModel):
    user_id: str


class User(BaseModel):
    fullName: str
    userRole: str
    activeStatus: str
    userId: str
