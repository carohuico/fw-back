from pydantic import BaseModel
from typing import List


class SaveFomulaTree(BaseModel):
    tree_json: dict

class Notes(BaseModel):
    entry: str


class UserData(BaseModel):
    user_id: str
    access: str
    formula_id: str


class ManageSharedAccess(BaseModel):
    add: List[UserData] = []
    edit: List[UserData] = []
    delete: List[UserData] = []


class fetchuser(BaseModel):
    username: str
