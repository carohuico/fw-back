from base64 import b64decode
from datetime import datetime, timedelta
from typing import Any
from passlib.context import CryptContext
from scripts.config import Service
from scripts.constants.app_constants import TableName
from scripts.core.handlers.user_handler import UserManagement
from scripts.core.handlers.plm_handler import PLMHandler

from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
from scripts.utils.sql_db_utils import DBUtility


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginHandler:
    def __init__(self):
        self.common_utils = CommonUtils()
        self.db_conn = DBUtility()
        self.tables = TableName()

    def login(self, user, server_token):
        try:
            logger.info("Inside login handler functionality")
            response = {
                "valid": "",
                "message": ""
            }

            # Declare variables
            valid = False
            message = ""
            current_timestamp = datetime.now()

            # Fetch username
            query = f""" Select * from {self.tables.frm_users} where username = %s """
            params = (user,)
            flag, data = self.db_conn.select_mysql_fetchone(query, params)

            # Check if user data exists
            if data:
                username_from_data = data.get("username", "")
                logger.info(f"User data found for username: {user}")
                # Check if user exists
                if str(username_from_data).lower() == str(user).lower():
                    plm_handler_obj = PLMHandler()
                    plm_valid = plm_handler_obj.validate_plm_user(user, token=server_token)
                    # plm_valid = True # Comment this after adding plm validation
                    if plm_valid:
                        active_status = data.get("activestatus", "y")
                        logger.info(f"Active status for user {user}: {active_status}")
                        if active_status == 'y':
                            logger.info(f"User {user} is active. Proceeding with login.")                            
                            update_query = f""" Update {self.tables.frm_users} set token = %s, lastlogin = %s where username = %s """
                            update_params = (server_token, current_timestamp, user)
                            update_flag = self.db_conn.update_mysql_table(update_query, update_params)

                            if update_flag:
                                valid = True
                                message = f" Login Successful "
                            else:
                                valid = False
                                message = f" Unable to update session for user: {user} "

                        # If user does not exist
                        else:
                            valid = False
                            message = f" The user {user} is inactive "

                    else:
                        valid = False
                        message = f" The user {user} does not exist"

                else:
                    valid = False
                    message = f" The user {user} is invalid "

            else:
                valid = False
                message = f" The user {user} is invalid "


            response.update({"valid": valid, "message": message, "data": data})

            logger.info("Completed login handler functionality")
            return response

        except Exception as e:
            logger.exception(e)
            raise e
