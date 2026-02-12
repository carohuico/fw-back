from fastapi import APIRouter, HTTPException, Request
from scripts.constants.app_routes import EndPoints, FormulaComparisonProject
from scripts.config import Configuration
from scripts.core.handlers.formula_comparison_handlers import FormulaComparisonHandler
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils


formula_comparison_router = APIRouter(prefix=EndPoints.app_base_url, tags=["FormulaComparison"])
conf_obj = Configuration()
formula_comp_handler_obj = FormulaComparisonHandler()
common_utils_obj = CommonUtils()

@formula_comparison_router.get(FormulaComparisonProject.get_formula_comparison_project_tree)
def get_formula_comparison_tree(project_id: str, request: Request):
    try:
        logger.info("Fetching formula comparison project tree")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_comp_handler_obj.get_formula_comparison_projects(username, project_id)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in get_formula_comparison_tree %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e

@formula_comparison_router.get(FormulaComparisonProject.search_local_formulas)
def search_local_formulas(ref_id: str, project_id:str, request:Request):
    try:
        logger.info("Searching for local formulas")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_comp_handler_obj.search_local_formulas(username, ref_id, project_id)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in search Local Formulas %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e

@formula_comparison_router.get(FormulaComparisonProject.create_formula_comparison_project)
def create_formula_comparison_project_service(formula_id: str, project_name: str, request: Request):
    try:
        logger.info("Creating formula comparison project")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)

        if valid:
            resp = formula_comp_handler_obj.create_formula_comparison_project(username, formula_id, project_name)
            return resp
        else:
            return {"status": "failed", "message": message}

    except Exception as e:
        logger.exception("Error in create_formula_comparison_project_service: %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e

@formula_comparison_router.post(FormulaComparisonProject.save_formula_comparison_project)
def save_comparison_project_service(input_json: dict, request: Request):
    try:
        logger.info("Saving changes in comparison project")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)

        if valid:
            resp = formula_comp_handler_obj.save_comparison_project(username, input_json)
            return resp
        else:
            return {"status": "failed", "message": message}

    except Exception as e:
        logger.exception("Error in save_comparison_project_service: %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e

@formula_comparison_router.post(FormulaComparisonProject.save_as_formula_comparison_project)
def save_as_comparison_project_service(input_json: dict, request: Request):
    try:
        logger.info("Creating a copy of comparison project formulas")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)

        if valid:
            resp = formula_comp_handler_obj.save_as_comparison_project(username, input_json)
            return resp
        else:
            return {"status": "failed", "message": message}

    except Exception as e:
        logger.exception("Error in save_comparison_project_service: %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e

@formula_comparison_router.post(FormulaComparisonProject.get_configuration)
def get_configuration(request: Request):
    try:
        logger.info("Fetching configurations")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_comp_handler_obj.get_configurations()
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in get_configurations %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e
