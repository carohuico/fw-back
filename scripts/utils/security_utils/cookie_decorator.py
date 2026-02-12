from typing import Optional

from fastapi import Request, Response
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.api_key import APIKeyBase, APIKeyCookie
from pydantic import BaseModel


class MetaInfoSchema(BaseModel):
    project_id: Optional[str] = ""
    user_id: Optional[str] = ""
    language: Optional[str] = ""


class MetaInfoCookie(APIKeyBase):
    """
    Project ID backend using a cookie.
    """

    scheme: APIKeyCookie
    cookie_name: str

    def __init__(self, cookie_name: str = "projectId"):
        super().__init__()
        self.model: APIKey = APIKey(**{"in": APIKeyIn.cookie}, name=cookie_name)
        self.cookie_name = cookie_name
        self.scheme_name = self.__class__.__name__
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)

    async def __call__(self, request: Request, response: Response):
        cookies = request.cookies
        cookie_json = {
            "projectId": cookies.get("projectId", cookies.get("project_id", request.headers.get("projectId"))),
            "userId": cookies.get("user_id", cookies.get("userId", request.headers.get("userId"))),
            "language": cookies.get("language", request.headers.get("language")),
        }
        return MetaInfoSchema(
            project_id=cookie_json["projectId"], user_id=cookie_json["userId"], language=cookie_json["language"]
        )

    @staticmethod
    def set_response_info(cookie_name, cookie_value, response: Response):
        response.set_cookie(cookie_name, cookie_value, samesite="strict", httponly=True)
        response.headers[cookie_name] = cookie_value
