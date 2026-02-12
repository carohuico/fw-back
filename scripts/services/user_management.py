from fastapi import APIRouter, status, Depends, Request, Response

from scripts.constants.app_routes import UserURL, RouteTags, EndPoints
from scripts.schemas.user_management import UserActions, UserDetails, DeleteUser, User
from scripts.core.handlers.user_handler import UserManagement
from scripts.logging import logger
from scripts.utils.security_utils.decorators import get_current_user
from scripts.utils.common_utils import CommonUtils
import traceback

user_management_router = APIRouter(prefix=EndPoints.app_base_url, tags=[RouteTags.user])
common_utils_obj = CommonUtils()

@user_management_router.post(UserURL.create_user)
def create_user_details_service(input_json: UserDetails, request: Request):
    try:
        logger.info("Inside create_user_details_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        
        if valid:
            resp = UserManagement().create_user_details(input_json)
            return resp
        else:
            return {'status': 'failed', 'message': message}

    except Exception as e:
        logger.error(f"Error creating user. Please try again later. : {str(e)}", exc_info=True)


@user_management_router.post(UserURL.delete_user)
def delete_user_service(input_json: DeleteUser, request: Request):
    try:
        logger.info("Inside delete_user_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = UserManagement().delete_user(input_json)
            return resp
        else:
            return {"status": "failed", "message": message}

    except Exception as e:
        logger.error(f"Error occurred while deleting the user : {str(e)}", exc_info=True)


@user_management_router.get(UserURL.fetch_users)
def fetch_users_service(input_json: str, request: Request):
    try:
        logger.info("Inside fetch_users_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = UserManagement().fetch_users(input_json, username)
            return resp
        else:
            return {'status': 'failed', 'message': message, 'data': list()}
        
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error occurred while fetching the user details : {str(e)}", exc_info=True)


@user_management_router.post(UserURL.edit_user)
def edit_user_details_service(input_json: User, request: Request):
    try:
        logger.info("Inside edit_user_details_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = UserManagement().edit_user_details(input_json)
            return resp
        else:
            return {'status': 'failed', 'message': message}

    except Exception as e:
        logger.error(f"Error Editing user.: {str(e)}", exc_info=True)

