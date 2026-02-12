"""
Define endpoints related to PLM operations (like fetching formula tree, syncing formula tree, fetching change orders etc.)
This will interact with PLMHandler for processing the requests and fetching data from PLM system.
"""
from typing import Optional

from fastapi import (
    APIRouter, Request
)
from scripts.constants.app_routes import EndPoints, RouteTags
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
from scripts.core.handlers.plm_handler import PLMHandler

plm_handler_obj = PLMHandler()
common_utils_obj = CommonUtils()
plm_router = APIRouter(prefix=EndPoints.app_base_url, tags=[RouteTags.plm])


@plm_router.post(EndPoints.search_server_formula_items)
def search_server_formula_items_service(request: Request, search_string: str, pagination_details: dict, req_attr: Optional[bool] = True):
    try:
        logger.info("Inside search_server_formula_items_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("Searching for formula items in PLM")
            return plm_handler_obj.search_server_formula_items(token, search_string, pagination_details, req_attr=req_attr)
        else:
            return {"status": "failed", "message": message}
    except Exception as err:
        logger.error(f"Exception while searching for formula items in PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.post(EndPoints.get_server_formula_tree)
def get_server_formula_tree_service(request: Request, item_number: str, bom: str, org: str, input_payload: Optional[dict] = None):
    try:
        logger.info("Inside get_server_formula_tree_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("Fetching formula items from PLM")
            return plm_handler_obj.get_server_formula_tree(token, username, item_number, bom, org, input_payload or dict())
        else:
            return {"status": "failed", "message": message}
    except Exception as err:
        logger.error(f"Exception while fetching formula tree from PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.post(EndPoints.sync_server_formula_tree)
def sync_server_formula_tree_service(request: Request, db_id: str, bom: str, org: str, req_data: dict):
    try:
        logger.info("Inside sync_server_formula_tree_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("sync formula to PLM" + str(db_id))
            return plm_handler_obj.sync_formula_tree(token, username, bom, org, req_data)
        else:
            return {"status": "failed", "message": message}
    except Exception as err:
        logger.error(f"Exception while sync formula to PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.post(EndPoints.search_server_formulas)
def search_server_formulas_service(ref_id: str, org: str, pagination_details: dict, request: Request):
    try:
        logger.info("Inside search_server_formulas_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("Searching for formula in PLM")
            return plm_handler_obj.search_server_formulas(token, ref_id, org, pagination_details)
        else:
            return {"status": "failed", "message": message}
    except Exception as err:
        logger.error(f"Exception while fetching server formula in PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.get(EndPoints.copy_formula_tree_from_server)
def copy_formula_tree_from_server_service(request: Request, item_number: str, bom: str, org: str, name: str):
    try:
        logger.info("Inside copy_formula_tree_from_server_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("Inside Copying formula tree from server service layer")
            return plm_handler_obj.copy_formula_tree_from_server(token, username, item_number, bom, org, name)
        else:
            return {"status": "failed", "message": message}
    except Exception as err:
        logger.error(f"Exception while fetching formula items from PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.post(EndPoints.pre_sync_server_formula_tree)
def pre_sync_server_formula_tree_service(request: Request, bom: str, org: str, req_data: dict):
    try:
        logger.info("Inside pre_sync_server_formula_tree_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("pre sync of formula")
            return plm_handler_obj.pre_sync_formula_tree(token, bom, org, req_data)
        else:
            return {"status": "failed", "message": "message"}
    except Exception as err:
        logger.error(f"Exception while pre sync formula to PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.post(EndPoints.get_all_draft_and_open_COs)
def get_all_draft_and_open_COs_service(request: Request, pagination_details: dict, org: str, item_id: str, search_text: Optional[str]=None):
    try:
        logger.info("Inside get_all_draft_and_open_COs_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("pre sync of formula")
            return plm_handler_obj.fetch_all_draft_and_open_COs(token, pagination_details, org, search_text, item_id)
        else:
            return {"status": "failed", "message": message}
    except Exception as err:
        logger.error(f"Exception while pre sync formula to PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.post(EndPoints.create_change_order)
def create_change_order_service(request: Request, name: str, desc: str, change_type: str, new_revision: str,
                                org: str, bom: str, formula_tree: dict):
    try:
        logger.info("Inside create_change_order_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("pre sync of formula")
            return plm_handler_obj.create_change_order(token, username, name, desc, change_type, new_revision, org, bom, formula_tree)
        else:
            return {"status": "failed", "message": "message"}
    except Exception as err:
        logger.error(f"Exception while pre sync formula to PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.post(EndPoints.sync_with_change_order)
def sync_with_change_order_service(request: Request, bom: str, org: str, co_details: dict, formula_tree: dict, new_revision: Optional[str]=None):
    try:
        logger.info("Inside sync_with_change_order_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            return plm_handler_obj.sync_with_change_order(token, username, bom, org, new_revision, co_details, formula_tree)
        else:
            return {"status": "failed", "message": message}
    except Exception as err:
        logger.error(f"Exception while sync formula to PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}


@plm_router.post(EndPoints.fetch_existing_item_COs)
def fetch_existing_item_COs_service(request: Request, pagination_details: dict, org: str, item_id: str, search_text: Optional[str]=None):
    try:
        logger.info("Inside fetch_existing_item_COs_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            logger.info("pre sync of formula")
            return plm_handler_obj.get_existing_change_orders(token, item_id, org, search_text, pagination_details)
        else:
            return {"status": "failed", "message": message}
    except Exception as err:
        logger.error(f"Exception while pre sync formula to PLM {str(err)}")
        return {"status": "failed", "message": err.args[0]}
