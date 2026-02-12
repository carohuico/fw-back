"""
    Module for user configuration
"""

import re
import time
from passlib.context import CryptContext
from scripts.constants import app_constants
from scripts.logging import logger
from scripts.utils.sql_db_utils import DBUtility
from scripts.utils.common_utils import CommonUtils
from scripts import constants
import traceback

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db_utility_obj = DBUtility()

class UserManagement:
    def __init__(self):
        self.db_conn = DBUtility()
        self.comm_utils_obj = CommonUtils()
        self.table_id_prefix = app_constants.TableIdPrefix()
        self.tables = app_constants.TableName()

    def validate_user(self, user, server_token):
        try:
            response = {
                "valid": "",
                "message": ""
            }

            # Declare variables
            valid = False
            message = ""
            current_timestamp = int(time.time())

            # Fetch username
            query = f""" Select * from {self.tables.frm_users} where username = '{user}' """
            flag, data = self.db_conn.select_mysql_fetchone(query)

            # Check user exists
            if flag:
                db_token = data.get("token", "")
                exp_time_stamp = data.get("last_login", "")

                if db_token:
                    if db_token == server_token:
                        if int(exp_time_stamp) > current_timestamp:
                            valid = True
                            message = f"The user {user} is valid"
                        else:
                            valid = False
                            message = f"The session is timed out"
                    else:
                        update_query = f""" Update {self.tables.frm_users} set token = {server_token} where user = {user}"""
                        update_flag = self.db_conn.update_mysql_table(update_query)
                        valid = True
                        message = f" The session has been updated for user {user} "
                else:
                    update_query = f""" Update {self.tables.frm_users} set token = {server_token} where user = {user}"""
                    update_flag = self.db_conn.update_mysql_table(update_query)
                    valid = True
                    message = f" The session has been updated for user {user} "
            
            # If user does not exist
            else:
                insert_query = f"""Insert into {self.tables.frm_users} values ({user}, {user + " " + user}, {user + "@" + "gmail.com"}, {server_token}, {current_timestamp})"""
                insert_flag = self.db_conn.insert_mysql_table(insert_query)
                if insert_flag:
                    valid = True
                    message = f" The session has been updated for user {user} "
            return response.update({"valid": valid, "message": message})

        except Exception as e:
            logger.error("Error occurred while validating the user : {}".format(str(e)))

    def fetch_users(self, status, username):
        try:
            logger.info("Inside fetch_users")
            if status == 'active':
                query = f"""select user_id as userId, CONCAT(UPPER(LEFT(name,1)),LOWER(RIGHT(name,LENGTH(name)-1))) as fullName, username as userName, role as userRole, createdby as createdBy, modifiedby as modifiedBy, lastLogin as lastLogin, 'Active' as activeStatus, createdon as createdOn, modifiedon as updatedOn from {self.tables.frm_users} where activestatus = 'y' and username <> '{username}' order by createdon desc"""
                message = "Active users fetched successfully"

            else:
                query = f""" select user_id as userId, CONCAT(UPPER(LEFT(name,1)),LOWER(RIGHT(name,LENGTH(name)-1))) as fullName, username as userName, role as userRole,createdby as createdBy, modifiedby as modifiedBy, lastLogin as lastLogin,'Inactive' as activeStatus, createdon as createdOn, modifiedon as updatedOn from {self.tables.frm_users} where activestatus = 'n' order by createdon desc """
                message = "Inactive users fetched successfully"
            flag, user_data = self.db_conn.select_mysql_table(query)
            if flag:
                logger.info("Completed fetch_users")
                return {'status': 'success', 'message': message,
                        'data': list(user_data)}
            else:
                return {'status': 'failed', 'message': 'unable to fetch users details', 'data': list()}

        except Exception as e:
            logger.error(f"Error while fetching the user details: {str(e)}")
            return {"error", "unable to fetch the user details"}

    def delete_user(self, input_json):
        try:
            logger.info("Inside delete_user")
            user_id = input_json.user_id
            query = f""" SELECT * FROM {self.tables.frm_users} WHERE user_id = '{user_id}' """
            flag, user_data = self.db_conn.select_mysql_table(query)

            if not user_data:
                logger.error("User not found")
                return {"status": "Failed", "message": "User details not found"}

            if user_data[0]["activestatus"] == 'n':  # 'N' represents that the user is already deleted
                logger.error("User already deleted")
                return {'status': 'failed', 'message': 'User details already deleted'}

            # Update the activestatus to 'N' for the given user_id
            query = f"""UPDATE {self.tables.frm_users} SET activestatus = 'n' WHERE user_id = '{user_id}'"""
            flag = self.db_conn.update_mysql_table(query)
            if flag:
                logger.info("Completed delete_user")
                return {"status": "success", "message": "User deleted Successfully"}
            else:
                return {"status": "failed", "message": " Unable to delete the user !!!"}

        except Exception as e:
            logger.error(f"Error occurred while deleting user : {str(e)}", exc_info=True)

    def create_user_details(self, user_data):
        try:
            logger.info("Inside create_user_details")
            query = f"SELECT user_id FROM {self.tables.frm_users} WHERE username = '{user_data.userName}'"
            flag, existing_user_data = self.db_conn.select_mysql_table(query)

            if flag and existing_user_data:
                logger.error("User already exists. Please choose a different username", exc_info=True)
                return {'status': 'failed', 'message': 'User already exists'}

            insert_query = """
            INSERT INTO frm_users (user_id, name, username, role, activestatus, createdon, modifiedon)
            VALUES ('{user_id}', '{name}', '{username}', '{role}', '{activestatus}', '{created_on}', '{modified_on}')
            """.format(
                user_id = self.comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_users),
                name = user_data.fullName,
                username = user_data.userName.lower(),
                role = user_data.userRole,
                activestatus = 'y',
                created_on = self.comm_utils_obj.time_stamp_generation(),
                modified_on = self.comm_utils_obj.time_stamp_generation()
            )
            flag = self.db_conn.insert_mysql_table(insert_query)
            
            if flag:
                resp = {'status': 'success', 'message': 'User added successfully'}
            else:
                resp = {'status': 'failed', 'message': 'Failed to add user'}

            logger.info("Completed create_user_details")
            return resp

        except Exception as e:
            logger.error("Error creating user")
            return {"status": "error", "message": "Error creating user"}

    def edit_user_details(self, input_json):
        try:
            logger.info("Inside edit_user_details")
            modified_on = self.comm_utils_obj.time_stamp_generation()
            query = f"""UPDATE {self.tables.frm_users} SET role='{input_json.userRole}', activestatus='{"y" if input_json.activeStatus.lower() == "active" else "n"}', name='{input_json.fullName}', modifiedon='{modified_on}' WHERE user_id='{input_json.userId}'"""
            flag = self.db_conn.update_mysql_table(query)

            # print(flag)
            if flag:
                resp = {'status': 'success', 'message': 'Details updated successfully'}
            else:
                resp = {'status': 'failed', 'message':  'Details not updated successfully'}
            
            logger.info("Completed edit_user_details")
            return resp
        except Exception as e:
            logger.error("Error editing user")
            return {"status": "error", "message": "Error editing user"}

