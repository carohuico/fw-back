import os
from typing import Optional

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
)
from scripts.config import Configuration
from scripts.constants.app_routes import EndPoints
from scripts.core.handlers.login_handler import LoginHandler
from scripts.logging import logger
from scripts.utils.security_utils.cookie_decorator import MetaInfoCookie

login_router = APIRouter(prefix=EndPoints.app_base_url, tags=["Login"])
login_handler = LoginHandler()
get_cookies = MetaInfoCookie()
# auth = CookieAuthentication()
conf_obj = Configuration()


@login_router.get(EndPoints.api_login)
def login(user: str, token: str, request: Request):
    final_json = {"status": "failed", "message": "Failed to login", "data": {}}
    try:
        # token_val = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        # username = str.replace(str(request.headers["user"]), "", "")
        logger.info("Inside login functionality")
        result = login_handler.login(user, token)
        if result.get("valid", ""):
            final_json.update({"status": "success", "message": result.get("message", ""), "data": result.get("data", {})})
        else:
            final_json.update({"message": result.get("message", "")})

        return final_json

    except Exception as e:
        logger.exception(str(e))
        final_json['message'] = str(e)
        raise HTTPException(status_code=401, detail=e.args, ) from e


# @login_router.get(EndPoints.api_get_token)
# def get_token(response: Response, t: Optional[str] = None):
#     return login_handler.get_token(response, t=t)


# @login_router.post(EndPoints.api_aad_login_uri)
# def get_aad_auth_uri(request: Request):
#     try:
#         data = login_handler.get_aad_auth_uri(request)
#         return {"status": "success", "data": data}
#     except Exception as e:
#         logger.exception(e)
#         return {"status": "failed", "message": str(e)}


# @login_router.post(EndPoints.api_aad_login)
# def aad_login(
#         token_payload: AzureActiveDirectoryUserRequest,
#         request: Request,
#         response: Response,
#         token=Cookie(None),
# ):
#     try:
#         resp = login_handler.aad_login_flow(token_payload.dict(), request, response, token)
#         if bool(resp):
#             return resp
#         else:
#             return {"status": "failed", "message": DefaultExceptionsCode.DE001}
#     except AzureADUserDoesNotExists as ae:
#         logger.warning(ae)
#         raise HTTPException(
#             status_code=403,
#             detail=ae.args,
#         ) from ae
#     except Exception as e:
#         logger.exception(e)
#         raise HTTPException(
#             status_code=401,
#             detail=e.args,
#         ) from e


# @login_router.post(EndPoints.api_saml_verify)
# def api_saml_verify(request: Request, SAMLResponse=Form(...)):
#     try:
#         resp = login_handler.saml_verify_flow(SAMLResponse, request)
#         if bool(resp):
#             return RedirectResponse(url=resp, status_code=status.HTTP_303_SEE_OTHER)
#         else:
#             return {"status": "failed", "message": DefaultExceptionsCode.DE001}
#     except Exception as e:
#         logger.exception(e)
#         raise HTTPException(
#             status_code=401,
#             detail=e.args,
#         ) from e


# @login_router.post(EndPoints.api_saml_login)
# def api_saml_login(
#         session_payload: SAMLSessionLoginRequest,
#         request: Request,
#         response: Response,
#         token=Cookie(None),
# ):
#     try:
#         resp = login_handler.retrieve_saml_user(session_payload, request, response, token)
#         if bool(resp):
#             return resp
#         else:
#             return {"status": "failed", "message": DefaultExceptionsCode.DE001}
#     except AzureADUserDoesNotExists as ae:
#         logger.warning(ae)
#         raise HTTPException(
#             status_code=403,
#             detail=ae.args,
#         ) from ae


# @login_router.get(EndPoints.api_saml_test_verify)
# def test_saml_verify():
#     try:
#         resp = login_handler.saml_test_verify_flow()
#         if bool(resp):
#             return RedirectResponse(resp)
#         else:
#             return {"status": "failed", "message": DefaultExceptionsCode.DE001}
#     except Exception as e:
#         logger.exception(e)
#         raise HTTPException(
#             status_code=401,
#             detail=e.args,
#         ) from e


# @login_router.post("/login_dev")
# def login_dev(
#         login_request: LoginRequest,
#         request: Request,
#         response: Response,
#         token: str = Cookie(...),
# ):
#     try:
#         unique_key = request.cookies.get("unique-key")
#         if unique_key is None:
#             unique_key = request.headers.get("unique-key")
#         return login_handler.login_flow(
#             login_request=login_request,
#             request=request,
#             response=response,
#             token=token,
#             enc=False,
#             unique_key=unique_key,
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=401,
#             detail=e.args,
#         ) from e


# @login_router.post(EndPoints.api_logout)
# def logout(request: Request):
#     """
#     This is the service to logout a current user
#     """
#     try:
#         session_id = request.cookies.get("session_id")
#         login_token = request.cookies.get("login-token")
#         if login_token is None:
#             login_token = request.headers.get("login-token")
#         refreshToken = request.cookies.get("refresh-token")
#         if refreshToken is None:
#             refreshToken = request.headers.get("refresh-token")
#         return login_handler.logout(session_id, login_token, refreshToken)
#     except Exception as e:
#         return DefaultFailureResponse(message="Failed to logout", error=str(e)).dict()


# @login_router.get(EndPoints.send_external_image)
# def send_external_image_path(request: Request):
#     try:
#         client_name = request.client.host
#         image_name = client_name.split(".")[0]
#         image_path = os.path.join(PathsToDirectories.IMAGE_PATH, "static", f"{image_name}.png")
#         if os.path.exists(image_path):
#             return FileResponse(image_path)
#     except Exception as e:
#         logger.error(e)
#     return {"status": "failed", "message": "Image not found"}


# @login_router.post(EndPoints.verify_mfa)
# def verify_mfa(
#         request_data: VerifyMFA,
#         request: Request,
#         response: Response,
#         token: str = Secrets.token,
# ):
#     try:
#         response = login_handler.verify_mfa(request_data, request, response, token)
#         return DefaultResponse(status="success", message="Success", data=response)
#     except Exception as e:
#         logger.exception(f"Error while verifying mfa {str(e)}")
#         return DefaultFailureResponse(message=DefaultExceptionsCode.DE002)


# @login_router.get(EndPoints.check_login)
# async def check_login(request: Request, project_id: Optional[str] = None, user_id=""):
#     resp = JSONResponse({"user_id": user_id})
#     project_id = request.cookies.get("projectId", project_id)
#     if not project_id:
#         raise HTTPException(status_code=204)
#     resp.set_cookie(
#         "projectId", project_id, httponly=True, secure=Service.secure_cookie, max_age=Service.cookie_timeout
#     )
#     resp.set_cookie("user_id", user_id, httponly=True, secure=Service.secure_cookie)
#     resp.set_cookie("userId", user_id, httponly=True, secure=Service.secure_cookie)
#     return resp
