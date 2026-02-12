from fastapi import APIRouter, HTTPException, Request
from scripts.constants.app_routes import EndPoints, HomePage
from scripts.config import Configuration
from scripts.utils.sql_db_utils import DBUtility
from scripts.core.handlers.home_handler import HomeHandler
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
from scripts.schemas.home_models import CreateFormula, NameDetails
from scripts.exceptions.fwb_exceptions import FWBHomeException, CustomException

home_router = APIRouter(prefix=EndPoints.app_base_url, tags=["HomePage"])
conf_obj = Configuration()
db_utility = DBUtility()
home_handler = HomeHandler()

common_utils_obj = CommonUtils()


@home_router.get(HomePage.fetch_development_formulae)
def fetch_development_formulae_service(formula_type: str, request: Request):
    """
        This method calls the function that will fetch the development formulae
    """
    try:
        logger.info("Inside fetch_development_formulae_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            result = home_handler.fetch_development_formulae(username, formula_type)
            if result.get("status", "") == "success":
                return result
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in fetch_development_formulae_service: %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@home_router.get(HomePage.fetch_formula_comparison_projects)
def fetch_formula_comparison_projects_service(request: Request):
    """
        This method calls the function that will fetch the formula comparison projects
    """
    try:
        logger.info("Inside fetch_formula_comparison_projects_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            result = home_handler.fetch_formula_comparison_projects(username)
            if result.get("status", "") == "success":
                return result
        else:
            return {"status": "failed", "message": message}

    except Exception as e:
        logger.exception("Error in fetch_formula_comparison_projects_service: %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@home_router.get(HomePage.fetch_shared_forumalae)
def fetch_shared_formulae_service(request: Request):
    """
        This method calls the function that will fetch the development formulae
    """
    try:
        logger.info("Inside fetch_shared_formulae_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            result = home_handler.fetch_shared_formulae(username)
            if result.get("status", "") == "success":
                return result

        else:
            return {"status": "failed", "message": message}

    except Exception as e:
        logger.exception("Error in fetch_shared_formulae_service: %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@home_router.delete(HomePage.delete_compairson_project)
def delete_compairson_project_service(comp_id: str, request: Request):
    """
        This method calls the function that will fetch the development formulae
    """
    try:
        logger.info("Inside delete_compairson_project_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            result = home_handler.delete_compairson_project(comp_id)
            if result.get("status", "") == "success":
                return result

        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in delete_compairson_project_service: %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@home_router.post(HomePage.create_formula)
def create_formula_service(payload: CreateFormula, request: Request):
    try:
        logger.info("Inside create_formula_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)

        if valid:
            formula_name = payload.formula_name
            data = payload.data
            result = home_handler.create_formula(formula_name, data, username)
            return result
        else:
            return {"status": "failed", "message": message, "data": ""}
    except Exception as e:
        logger.exception(str(e))
        raise e


@home_router.get(HomePage.delete_development_formulae)
def delete_development_formula_service(formula_id: str, request: Request):
    """
        This method calls the function that will delete the development formulae
    """
    try:
        logger.info("Inside delete_development_formula_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)

        if valid:
            """result = home_handler.delete_development_formulae(formula_id) to be commented"""
            result = {"status": "success", "message": "This api yet to be developed...", "data": []}
            return result

        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception(str(e))


@home_router.post(HomePage.name_details)
def formula_details(input_json: NameDetails, request: Request):
    try:
        logger.info("Inside formula_details")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = home_handler.fetch_name_details(username, input_json)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@home_router.get(HomePage.update_formula_status)
def update_formula_status_service(formula_id: str, status: str, request: Request):
    try:
        logger.info("Inside update_formula_status_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = home_handler.update_formula_status_handler(formula_id, status)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in update_formula_status_service, %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e
