from pydantic import BaseModel
from typing import Optional


class GetServerFormulaModel(BaseModel):
    type: Optional[str] = None
    db_id: Optional[str] = None
    root_db_id: Optional[str] = None


class SyncWithCOModel(BaseModel):
    CO: dict
    formula_tree: dict
