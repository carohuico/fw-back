import re

from fastapi import HTTPException
from werkzeug.utils import secure_filename
from scripts.logging import logger
# from scripts.schemas.login import TokenVal
from scripts.utils.sql_db_utils import DBUtility
import os
import base64
from scripts.config import PathsToDirectories
import uuid
import traceback
from datetime import datetime


class CommonUtils:

    def __init__(self):
        self.db_conn = DBUtility()

    def unique_id_generator(self, doc_type, prefix=True):
        """

            :param doc_type:
            :param prefix:
            :return:
        """
        try:
            if not prefix:
                uid = '{}'.format(str(uuid.uuid4().hex))
            else:
                uid = '{}_{}'.format(doc_type.replace("-", ""), str(uuid.uuid4().hex))
            return uid

        except Exception as e:
            status_message = "Failed in UID genration: ", str(e)
            logger.exception(status_message)

    def token_validation(self, user, token):
        try:
            valid = False
            message = "Invalid User" 

            query = f""" SELECT token FROM frm_users WHERE username = '{user}' """
            flag, data = self.db_conn.select_mysql_fetchone(query)
            # print("Data: ", data)
            # data = dat[0]

            if data:
                db_token = data.get("token", "")
                if token == db_token:
                    valid = True
                    message = "Valid User" 
                    
                else:
                    valid = False
                    message = "Invalid Token" 

            else:
                valid = False
                message = "Invalid User" 
            
            return valid, message

        except Exception as e:
            traceback.print_exc()
            logger.exception(str(e))

    @staticmethod
    def get_bool_value(val):
        """
            Gets the boolean value derived from a list of values
        """
        try:
            response = False
            if int(val) in [1]:
                response = True

            return response
        except Exception as es:
            logger.exception(str(es))

    def time_stamp_generation(self):
        try:
            current_date = datetime.now()
            iso_formatted_str = current_date.isoformat(timespec='milliseconds')
            return datetime.fromisoformat(iso_formatted_str)
        except Exception as e:
            logger.exception("Error in children_insertion: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e
