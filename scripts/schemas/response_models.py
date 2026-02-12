from typing import Any, Optional

from pydantic import BaseModel


class DefaultResponse(BaseModel):
    status: str = "failed"
    message: Optional[str]
    data: Optional[Any]


class MetaTagResponse(DefaultResponse):
    end: bool


class DefaultFailureResponse(DefaultResponse):
    error: Any


class MobileDefaultResponse(BaseModel):
    status: bool = True
    message: Optional[str] = ""
    data: Optional[Any]


class MobileFailureResponse(BaseModel):
    status: bool = False
    message: Optional[str] = ""
    data: Optional[Any] = {}
    error: Optional[str] = ""


class SiteHierarchyResponse(BaseModel):
    status: str = "Failed"
    message: Optional[str]
    site_hierarchy_data: Optional[Any]


class DefaultScenarioParameterResponse(BaseModel):
    status: str = "failed"
    message: Optional[str]
    data: Optional[Any]
    timestamp: Optional[dict]
