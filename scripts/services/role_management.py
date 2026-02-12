from fastapi import APIRouter, status, Request

from scripts.constants.app_routes import RoleURL, RouteTags, EndPoints
from scripts.core.handlers.role_management_handler import RoleManagement
from scripts.schemas.role_management_models import UserDetails, RoleDetails
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
import traceback

role_management_router = APIRouter(prefix=EndPoints.app_base_url, tags=[RouteTags.role])
role_management_obj = RoleManagement()
common_utils_obj = CommonUtils()

@role_management_router.get(RoleURL.fetch_roles)
def get_role_access_service(request: Request):
    try:
        logger.info("Inside get_role_access_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = role_management_obj.get_role_access()
            # traceback.print_exc()
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error occurred while fetching the roles details : {str(e)}", exc_info=True)


@role_management_router.get(RoleURL.fetch_access)
def get_access_service(username: str, role: str, request: Request):
    try:
        logger.info("Inside get_access_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        user = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(user, token)
        if valid:
            resp = role_management_obj.get_access(username, role)
            # traceback.print_exc()
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error occurred while fetching the userroles and accessTo details : {str(e)}", exc_info=True)



@role_management_router.post(RoleURL.create_UserRole)
def create_user_role_details_service(input_json: UserDetails, request: Request):
    try:
        logger.info("Inside create_user_role_details_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = role_management_obj.create_user_role_details(input_json)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error creating UserRole. Please try again later. : {str(e)}", exc_info=True)


@role_management_router.post(RoleURL.edit_UserRole)
def edit_user_role_details_service(input_json: RoleDetails, request: Request):
    try:
        logger.info("Inside edit_user_role_details_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = role_management_obj.edit_user_role_details(input_json)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error creating UserRole. Please try again later. : {str(e)}", exc_info=True)


@role_management_router.get(RoleURL.fetch_UserRole_List)
def fetch_user_role_list_details_service(request: Request):
    try:
        logger.info("Inside fetch_user_role_list_details_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = role_management_obj.fetch_user_role_list_details()
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error fetching UserRole. Please try again later. : {str(e)}", exc_info=True)


@role_management_router.get(RoleURL.fetch_access_features)
def fetch_access_features_service(request: Request):
    try:
        logger.info("Inside fetch_access_features_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = role_management_obj.fetch_access_features()
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error fetching access features. : {str(e)}", exc_info=True)
