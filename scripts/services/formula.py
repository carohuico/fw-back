from fastapi import APIRouter, HTTPException, Request
from scripts.schemas.formula_models import SaveFomulaTree, Notes, ManageSharedAccess
from scripts.constants.app_routes import EndPoints, Formula
from scripts.config import Configuration
from scripts.utils.common_utils import CommonUtils
from scripts.core.handlers.formula_handlers import FormulaHandler
from scripts.logging import logger

formula_router = APIRouter(prefix=EndPoints.app_base_url, tags=["Formula"])
conf_obj = Configuration()
formula_handler_obj = FormulaHandler()
common_utils_obj = CommonUtils()


@formula_router.get(Formula.get_local_formula_tree)
def get_formula_tree_service(id: str, request:Request):
    try:
        logger.info("Fetching formula tree JSON data")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_handler_obj.get_formula_details_service(id)

            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in get_formula_tree_service %s", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@formula_router.post(Formula.save_formula_tree)
def save_formula_tree(input_json: SaveFomulaTree, request:Request):
    try:
        logger.info("Saving changes in formula tree")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_handler_obj.save_formula_tree_handler(username, input_json.tree_json)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in save_formula_tree service", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@formula_router.post(Formula.save_formula_tree_as)
def save_formula_tree_as(name: str, input_json: SaveFomulaTree, request: Request):
    try:
        logger.info("Creating a copy of a formula")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_handler_obj.save_formula_tree_as(username, name, input_json.tree_json)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in get_attribute_definitions", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@formula_router.get(Formula.get_entry)
def fetch_notes(db_id: str, request: Request):
    try:
        logger.info("Fetching notes for the formula")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_handler_obj.fetch_notes_handler(db_id)
            return resp
        else:
            return {"status": "failed", "message": message}

    except Exception as e:
        logger.exception("Error in get_notes", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@formula_router.post(Formula.post_entry)
def post_notes(formula_id: str, entry_json: Notes, request: Request):
    try:
        logger.info("Inside post_notes")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_handler_obj.insertion_notes_handler(formula_id, entry_json.entry, username)

            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in get_notes", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@formula_router.post(Formula.manage_shared_access)
def manage_shared_access_service(input_json: ManageSharedAccess, request: Request):
    try:
        logger.info("Inside manage_shared_access_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_handler_obj.manage_shared_access(input_json)
            return resp
        else:
            return {"status": "failed", "message": message}

    except Exception as e:
        logger.error("Error in shared access part", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@formula_router.get(Formula.fetch_access_info)
def fetch_access_info_service(formula_id: str, request: Request):
    try:
        logger.info("Inside fetch_access_info_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_handler_obj.fetch_access_info(formula_id)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in shared access part", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@formula_router.get(Formula.fetch_username_data)
def fetch_username_info_service(formulaid: str, request: Request):
    try:
        logger.info("Inside fetch_username_info_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = formula_handler_obj.fetch_username_data(username, formulaid)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in fetching details", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@formula_router.post(Formula.get_excel_report, responses={200: {"status": "success", "message": "File Downloaded "
                                                                                                "SuccessFully"}})
def get_excel_report(formula_json: dict, request: Request):
    try:
        logger.info("Inside get_excel_report")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            return formula_handler_obj.excel_generator_handler(formula_json)
        else:
            return {"status": "failed", "message": "Unable to download the excel file"}
    except Exception as e:
        logger.exception("Error while generating excel sheet", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e
