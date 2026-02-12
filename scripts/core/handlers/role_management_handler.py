import re
from copy import deepcopy
import time
from passlib.context import CryptContext
from scripts.logging import logger
from scripts.utils.sql_db_utils import DBUtility
from scripts.utils.common_utils import CommonUtils
from scripts.constants.app_constants import TableIdPrefix, TableName
import traceback

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db_utility_obj = DBUtility()
comm_utils_obj = CommonUtils()


class RoleManagement:
    def __init__(self):
        self.db_conn = DBUtility()
        self.table_id_prefix = TableIdPrefix()
        self.tables = TableName()

    def get_role_access(self):
        try:
            logger.info("Inside get_role_access")
            query_fetch_user_access = f""" select id, role, access from {TableName.frm_user_roles} """
            flag, resp_query_fetch_user_access = self.db_conn.select_mysql_table(query_fetch_user_access)

            query_feature_access = f""" select access_value, access_label from {TableName.frm_feature_access} """
            flag, resquery_feature_access = self.db_conn.select_mysql_table(query_feature_access)
            result = []

            access_label_dict = {rec['access_value'].strip(): rec['access_label'].strip() for rec in
                                 resquery_feature_access}
            print(access_label_dict)

            for rec in resp_query_fetch_user_access:
                d = {}
                d['roleId'] = rec["id"]
                d['roleName'] = rec["role"]
                access_items = rec['access'].replace('\xa0', '').split(',')

                access_list = []
                access_label_dict_keys = list(access_label_dict)
                for item in access_items:
                    stripped_item = item.strip()
                    if stripped_item in access_label_dict_keys:
                        access_list.append({"key": stripped_item, "label": access_label_dict[stripped_item]})
                    else:
                        print(f"'{stripped_item}' not found in access labels.")

                d["accessTo"] = access_list
                result.append(d)
            response = {
                "status": "success",
                "message": "Details fetched successfully",
                "data": result
            }

            logger.info("Completed get_role_access")
            return response
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            print(e)
            return response

    def get_access(self, username, role):
        try:
            logger.info("Inside get_access")
            role_query = f""" select role, access from {self.tables.frm_user_roles} where role = %s """
            role_query_param = (role,)
            flag, resp_user_data = self.db_conn.select_mysql_table(role_query, role_query_param)

            query_feature_access = f"select access_value, access_label from {self.tables.frm_feature_access}"
            flag, resquery_feature_access = self.db_conn.select_mysql_table(query_feature_access)

            access_label_dict = {rec['access_value'].strip(): rec['access_label'].strip() for rec in
                                 resquery_feature_access}

            result = []

            for rec in resp_user_data:
                access_items = rec['access'].replace('\xa0', '').split(',')
                access_list = []

                access_label_dict_keys = list(access_label_dict)

                for item in access_items:
                    stripped_item = item.strip()
                    if stripped_item in access_label_dict_keys:
                        access_list.append({"key": stripped_item, "label": access_label_dict[stripped_item]})
                    else:
                        print(f"'{stripped_item}' not found in access labels.")

                result.extend(access_list)

            logger.info("Completed get_access")
            return {"status": "success", "message": "Details fetched successfully", "data": result}

        except Exception as e:
            traceback.print_exc()
            logger.error("Error fetching details")
            return {"status": "error", "message": "Error fetching the details"}

    def create_user_role_details(self, user_data):
        try:
            logger.info("Inside create_user_role_details")
            role_id = comm_utils_obj.unique_id_generator(TableIdPrefix.frm_user_roles)
            role_name = user_data.roleName

            query = f""" SELECT id FROM {self.tables.frm_user_roles} WHERE role = %s"""
            query_param = (role_name,)
            flag, existing_user_data = self.db_conn.select_mysql_table(query, query_param)
            if flag and existing_user_data:
                logger.error("User Role already exists. Please choose a different RoleName", exc_info=True)
                return {'status': 'failed', 'message': 'User Role already exists'}

            access_values = [item["value"] for item in user_data.accessTo]

            access_values_str = ', '.join(access_values)
            # Build the INSERT query for user roles
            roles_insert_query = f""" INSERT INTO {self.tables.frm_user_roles} (id, role, access) VALUES (%s, %s, %s) """

            roles_insert_query_param = (role_id, role_name, access_values_str)

            flag = self.db_conn.insert_mysql_table(roles_insert_query, roles_insert_query_param)

            logger.info("Completed create_user_role_details")
            if flag:
                resp = {'status': 'success', 'message': 'UserRole and Access added successfully'}
                return resp
            else:
                resp = {'status': 'failed', 'message': 'Failed to add UserRole and Access'}
                return resp
        except Exception:
            traceback.print_exc()
            return {"status": "error", "message": "Error creating UserRole"}

    def edit_user_role_details(self, input_json):
        try:
            logger.info("Inside edit_user_role_details")
            # Check if the given role_id exists
            user_role_id = input_json.id
            user_role_name = input_json.roleName

            role_query = f""" SELECT * FROM {self.tables.frm_user_roles} WHERE id = %s """
            role_query_param = (user_role_id,)
            flag, existing_role_data = self.db_conn.select_mysql_table(role_query, role_query_param)

            if not flag or not existing_role_data:
                logger.error(f"Role with id {input_json.id} not found.", exc_info=True)
                return {'status': 'failed', 'message': f"Role with id {input_json.id} not found"}

            # Update roleName and accessTo based on updated_data
            access_values = [item["value"] for item in input_json.accessTo]
            access_values_str = ', '.join(access_values)

            # Build the UPDATE query for user roles
            update_query = f""" UPDATE {self.tables.frm_user_roles} SET role = %s, access = %s WHERE id = %s """
            update_query_param = (user_role_name, access_values_str, user_role_id)
            flag = self.db_conn.update_mysql_table(update_query, update_query_param)

            logger.info("Completed edit_user_role_details")
            if flag:
                resp = {'status': 'success', 'message': 'UserRole updated successfully'}
                return resp
            else:
                resp = {'status': 'failed', 'message': 'Failed to update UserRole'}
                return resp
        except Exception:
            traceback.print_exc()
            return {"status": "error", "message": "Error editing UserRole"}

    def fetch_user_role_list_details(self):
        try:
            logger.info("Inside fetch_user_role_list_details")
            query = f"""SELECT role FROM {self.tables.frm_user_roles}"""
            flag, user_data = self.db_conn.select_mysql_table(query)

            if flag:
                roles = [row['role'] for row in user_data]
                return {'status': 'success', 'message': 'User Roles fetched successfully', 'data': roles}
            else:
                return {'status': 'failed', 'message': 'Unable to fetch User Role details', 'data': []}
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error while fetching the User Role details: {str(e)}")
            return {'status': 'error', 'message': 'Unable to fetch the User Role details', 'data': []}

    def fetch_access_features(self):
        try:
            logger.info("Inside fetch_access_features")
            fa_query = f"""SELECT access_value as value, access_label as label FROM {self.tables.frm_feature_access}"""
            fa_flag, fa_data = self.db_conn.select_mysql_table(fa_query)

            logger.info("Completed fetch_access_features")
            if fa_data:
                # roles = [row['role'] for row in user_data]
                return {'status': 'success', 'message': 'Access Features fetched successfully', 'data': fa_data}
            else:
                return {'status': 'failed', 'message': 'Unable to fetch Access Features', 'data': []}
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in fetch_access_features: {str(e)}")
            # return {'status': 'error', 'message': 'Unable to fetch_access_features', 'data': []}
