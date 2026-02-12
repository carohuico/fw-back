from fastapi import APIRouter, HTTPException, Request, UploadFile, Form, File
from scripts.constants.app_routes import TableConfig, EndPoints
from scripts.config import Configuration
from scripts.core.handlers import table_config_handler
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
from scripts.schemas.table_config_models import ExcelConfigName

table_config_router = APIRouter(prefix=EndPoints.app_base_url, tags=["Table Configuration"])
conf_obj = Configuration()

table_config_obj = table_config_handler.TableConfig()
common_utils_obj = CommonUtils()


@table_config_router.get(TableConfig.get_attribute_definitions)
def get_attribute_definition_service(formulaid: str, request: Request):
    try:
        logger.info("Inside get_attribute_definition_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")
        valid, message = common_utils_obj.token_validation(username, token)
        if valid:

        # username = "usernew"
            resp = table_config_obj.get_attribute_definition(username, formulaid)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.exception("Error in get_attribute_definitions", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@table_config_router.post(TableConfig.upload_config_json)
async def upload_config_json_service(request: Request, configName: str, file: UploadFile=Form(...)):
    try:
        logger.info("Inside upload_config_json_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = await table_config_obj.upload_config_json(username, file, configName)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in fetching details", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@table_config_router.post(TableConfig.upload_config_record)
async def upload_config_record_service(file: UploadFile, id: str, request: Request):
    try:
        logger.info("Inside upload_config_record_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            resp = await table_config_obj.upload_config_record(file, id)
            return resp
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in fetching details", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@table_config_router.get(TableConfig.download_config_json,
                         responses={200: {"status": "success", "message": "File Downloaded Successfully"}})
def download_config_json_service(request: Request, configName: str):
    try:
        logger.info("Inside download_config_json_service")
        # token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        # username = str.replace(str(request.headers["user"]), "", "")

        # response = Response()
        # response.headers["status"] = "success"
        # response.headers["message"] = "File Download Successfully"

        # valid, message = common_utils_obj.token_validation(username, token)
        if True:
            result = table_config_obj.download_config_json(configName)
            return result
        else:
            return {"status": "failed", "message": "message"}

    except Exception as e:
        logger.error("Error in downloading the config json file", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e

@table_config_router.get(TableConfig.fetch_download_json_data)
def fetch_download_json_data_service(request: Request):
    try:
        logger.info("Inside fetch_download_json_data_service")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            result = table_config_obj.fetch_download_json_data()
            return result
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in Fetching the data", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e


@table_config_router.post(TableConfig.add_excel_conf_name)
def add_configuration_name(payload: ExcelConfigName, request:Request):
    try:
        logger.info("Inside add_configuration_name")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            result = table_config_obj.excel_conf_name_insrt(payload.excel_conf_name, username)
            return result
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in add_configuration_name", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e

@table_config_router.get(TableConfig.fetch_excel_config)
def fetch_excel_configs(request:Request):
    try:
        logger.info("Inside fetch_excel_configs")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            result = table_config_obj.fetch_excel_conf()
            return result
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in fetch_excel_configs", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e

@table_config_router.get(TableConfig.delete_excel_config)
def delete_excel_config(db_id: str, request:Request):
    try:
        logger.info("Inside delete_excel_config")
        token = str.replace(str(request.headers["Authorization"]), "Bearer ", "")
        username = str.replace(str(request.headers["user"]), "", "")

        valid, message = common_utils_obj.token_validation(username, token)
        if valid:
            result = table_config_obj.delete_excel_config(db_id)
            return result
        else:
            return {"status": "failed", "message": message}
    except Exception as e:
        logger.error("Error in delete_excel_config", str(e))
        raise HTTPException(status_code=401, detail=e.args, ) from e
