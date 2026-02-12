import json
import traceback
from fastapi import HTTPException, Response
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
from scripts.constants.app_constants import ResponseMessage, HomePage, TableIdPrefix, TableName, ConfigConstants
from scripts.utils.sql_db_utils import DBUtility
from datetime import datetime

# db_utility = DBUtility()
app_constants_obj = HomePage()
comm_utils_obj = CommonUtils()


class TableConfig:
    def __init__(self):
        self.db_conn = DBUtility()
        self.table_id_prefix = TableIdPrefix()
        self.tables = TableName()

    def get_user_id(self, user):
        try:
            user_id_query = f""" Select user_id from {self.tables.frm_users} where username = %s"""
            flag, user_id_data = self.db_conn.select_mysql_fetchone(user_id_query, (user,))

            user_id = user_id_data.get("user_id", "") if user_id_data else ''
            return user_id

        except Exception as e:
            logger.error("Error in get_user_id: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def get_attribute_definition(self, username, formulaid):
        try:
            logger.info("Inside get_attribute_definition")
            response = ResponseMessage.final_json("failed", "unable to fetch the details", [])
            result = []
            is_enabled_status = False

            # Load config attr table data
            data_query = f""" Select cn.config from {self.tables.frm_configurations} cn where cn.is_enabled = {True} and cn.name = '{ConfigConstants.attribute_file_name}' """

            flag, data = self.db_conn.select_mysql_table(data_query)
            if data:
                config_data = data[0] if data else dict()
                config_json = config_data.get("config", [])

                result = json.loads(config_json)

            # Check if the id prefix is for comparison project or development formula
            id_prefix = formulaid.split("_")[0]
            if id_prefix == self.table_id_prefix.frm_comp_project:
                response = {"status": "success", "message": "Details fetched successfully", "data": result, "is_enabled": True}
            
            else:
                # Check if the formula is archived
                form_type_query = f""" Select * from {self.tables.frm_formula_attributes} where value = 'Archived' and fk_formula = %s """
                form_type_flag, form_type_data = self.db_conn.select_mysql_table(form_type_query, (formulaid,))

                if form_type_data:
                    response = {"status": "success", "message": "Details fetched successfully", "data": result, "is_enabled": False}
                    return response

                # Check user access
                user_access_query = f""" Select fsu.access from {self.tables.frm_shared_users} fsu INNER JOIN {self.tables.frm_users} fu ON fsu.user_id = fu.user_id where fsu.formulaid = '{formulaid}' AND fu.username = '{username}' AND fsu.access = 'editor' """
                creator_access_query = f""" Select * from {self.tables.frm_formula} ff INNER JOIN {self.tables.frm_users} fu ON ff.created_by = fu.user_id where fu.username = '{username}' and ff.id = '{formulaid}' """

                user_access_flag, user_access_data = self.db_conn.select_mysql_table(user_access_query)
                creator_access_flag, creator_access_data = self.db_conn.select_mysql_table(creator_access_query)

                if user_access_data or creator_access_data:
                    is_enabled_status = True

                # data_query = f""" Select cn.config from {TableName.frm_configurations} cn INNER JOIN {TableName.frm_users} usr ON cn.user_id = usr.user_id where username = '{username}' """
                    # response = ResponseMessage.final_json("success", "Details Fetched successfully", result)

                response = {"status": "success", "message": "Details fetched successfully", "data": result, "is_enabled": is_enabled_status}

            logger.info("Completed get_attribute_definition")
            return response
        except Exception as e:
            logger.exception("Error in get_attribute_definition handler ", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    async def upload_config_json(self, username, file, config_name):
        try:
            logger.info("Inside upload_config_json")
            user_id = self.get_user_id(username)
            if not file.filename.endswith(".json"):
                return HTTPException(status_code=400, detail="Only JSON files are allowed.")

            # Load file data
            content = await file.read()
            data = json.loads(content)
            filename = config_name.lower()
            # Fetch userid from the username
            user_query = f""" Select user_id from {self.tables.frm_users} where username = %s """
            user_query_param = (username,)

            user_flag, user_data = self.db_conn.select_mysql_fetchone(user_query, user_query_param)

            if config_name == "attributes":
                # if not isinstance(data, list) or not data:
                #     return HTTPException(status_code=400, detail="Invalid JSON format.")
                #
                # for obj in data:
                #     if not isinstance(obj,
                #                       dict) or not obj or "headerName" not in obj or "attributeGroupType" not in obj:
                #         return HTTPException(status_code=400,
                #                              detail="Invalid JSON format.")
                update_query = f""" UPDATE {self.tables.frm_configurations} SET is_enabled = %s WHERE name = %s
                                AND is_enabled = %s
                            """
                update_query_params = (False, filename, True)
                old_rec_flag = self.db_conn.update_mysql_table(update_query, update_query_params)

                # New data for insertion
                rec_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_configurations)
                config_data = json.dumps(data)

                # Insert a new record with new file data
                insert_query = f""" INSERT INTO {self.tables.frm_configurations} (id, name, user_id, is_enabled, config)
                            VALUES (%s, %s, %s, %s, %s) """
                insert_query_params = (rec_id, filename, user_id, True, config_data)

                flag = self.db_conn.insert_mysql_table(insert_query, insert_query_params)

            else:
                update_query = f"""update {self.tables.frm_excel_configurations} set config = %s, 
                                last_modified_by=%s, last_modified_date=%s  where name=%s """
                config_data = json.dumps(data)
                update_params = (config_data, user_id, self.time_stamp_generation(), filename)
                flag = self.db_conn.update_mysql_table(update_query, update_params)
                # return HTTPException(status_code=400, detail="Invalid config_name")

            # Update old records

            if flag:
                resp = {'status': 'success', 'message': 'JSON file read and stored successfully'}
            else:
                resp = {'status': 'failed', 'message': 'Failed to read json file'}

            logger.info("Completed upload_config_json")
            return resp
        except Exception as e:
            logger.error(f"Error while fetching the JSON file: {str(e)}")
            return {'status': 'failed', 'message': 'Unable to fetch the JSON file'}

    async def upload_config_record(self, file, id):
        try:
            logger.info("Inside upload_config_record")
            filename = ConfigConstants.attribute_file_name

            if not file.filename.endswith(".json"):
                return HTTPException(status_code=400, detail="Only JSON files are allowed.")

            content = await file.read()
            data = json.loads(content)

            query_id_exists = f"""SELECT id FROM {self.tables.frm_configurations} WHERE id = %s"""
            id_exists = self.db_conn.insert_mysql_table(query_id_exists, (id,))

            if not id_exists:
                return HTTPException(status_code=404, detail=f"Config record with ID {id} not found.")

            update_query = f""" UPDATE {self.tables.frm_configurations} SET config = %s, name = %s WHERE id = %s """

            config_data = json.dumps(data)
            update_query_param = (config_data, filename, id)

            flag = self.db_conn.insert_mysql_table(update_query, update_query_param)

            if flag:
                resp = {'status': 'success', 'message': f'Config record with ID {id} updated successfully'}
            else:
                resp = {'status': 'failed', 'message': f'Failed to update config record with ID {id}'}

            logger.info("Completed upload_config_record")
            return resp
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error while updating the config JSON record: {str(e)}")
            return {'status': 'error', 'message': 'Unable to update config JSON record'}

    def download_config_json(self, config_name):
        try:
            logger.info("Inside download_config_json")
            config_name = config_name.lower()
            if config_name == "attributes":
                query = f"""SELECT name, config FROM {TableName.frm_configurations} WHERE is_enabled = TRUE AND name = '{ConfigConstants.attribute_file_name}'"""
            # elif config_name == "excel":
            #     query = f"""SELECT name, config FROM {TableName.frm_configurations} WHERE is_enabled = TRUE AND name = '{ConfigConstants.excel_file_name}'"""
            else:
                query = f"""select name, config from {TableName.frm_excel_configurations} where 
                            lower(name)='{config_name}' """
                # return Response({"status": "error", "message": "Invalid config_name"}, status_code=400)

            flag, result = self.db_conn.select_mysql_table(query)

            if result:
                config_data = result[0]["config"]
                name = result[0]["name"]

                response_data = json.loads(config_data)
                final_data = json.dumps(response_data, indent=4)
                file_name = f"{name}.json"
                # with open(file_name, "w") as file:
                #     file.write(final_data)

                headers = {"status": "success", "message": "File Downloaded successfully",
                           'Content-Disposition': f'attachment; filename="{file_name}"'}

            else:

                return Response({"status": "error", "message": "Config data not found"}, status_code=404)

            logger.info("Completed download_config_json")
            return Response(final_data, headers=headers, media_type='application/json')

        except Exception as e:
            logger.error("Error in download_config_json: %s", str(e))
            raise HTTPException(status_code=500, detail="Internal server error") from e

    def fetch_download_json_data(self):
        try:
            logger.info("Inside fetch_download_json_data")
            query = f"""select c.id, c.user_id, c.name, c.is_enabled, c.config,
                                u.name as fullname, u.username
                                from {self.tables.frm_configurations} as c
                                inner join {self.tables.frm_users} as u ON c.user_id = u.user_id 
                                where c.name ='{ConfigConstants.attribute_file_name} """

            flag, data = self.db_conn.select_mysql_table(query)

            if data:
                configurations = []
                for row in data:
                    config_str = row['config']
                    if config_str is not None and isinstance(config_str, bytes):
                        config_str = config_str.decode('utf-8')
                    config_json = json.loads(config_str.replace('\n', ''))
                    config_data = {
                        'id': row['id'],
                        'user_id': row['user_id'],
                        'name': row['name'],
                        'is_enabled': bool(row['is_enabled']),
                        'config': config_json,
                        'fullname': row['fullname'],
                        'username': row['username']
                    }
                    configurations.append(config_data)
                return {"status": "success", "message": "Data Fetched SuccessFully", "data": configurations}
            else:
                return {'status': 'failed', 'message': 'error in fetching the data'}
        except Exception as e:
            logger.error("Error in fetch_data: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args) from e

    def time_stamp_generation(self):
        try:
            current_date = datetime.now()
            iso_formatted_str = current_date.isoformat(timespec='milliseconds')

            """current_date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]"""
            return datetime.fromisoformat(iso_formatted_str)

        except Exception as e:
            logger.exception("Error in children_insertion: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def excel_conf_name_validation(self, name):
        try:
            query = f"""select * from {self.tables.frm_excel_configurations} where lower(name) = %s"""
            query_params = (name,)
            flag, data = self.db_conn.select_mysql_fetchone(query, query_params)
            if flag and data:
                return True
            return False
        except Exception as e:
            logger.exception("Error in children_insertion: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def excel_conf_name_insrt(self, name, username):
        try:
            logger.info("Inside excel_conf_name_insrt")
            response = ResponseMessage.final_json("failed", "Unable to Save the Data")
            if self.excel_conf_name_validation(name):
                return {"status": "failed", "message": "Config Name Already Exists. Try Creating with Another Name",
                        "data": []}
            insert_query = f"""insert into {self.tables.frm_excel_configurations}(id, name, user_id, config, 
                                created_by, created_date, last_modified_by, last_modified_date) 
                                values(%s, %s, %s, %s, %s, %s, %s, %s)"""
            rec_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_excel_configs)
            user_id = self.get_user_id(username)
            insert_query_params = (
            rec_id, name, user_id, None, user_id, self.time_stamp_generation(), user_id, self.time_stamp_generation())
            flag = self.db_conn.insert_mysql_table(insert_query, insert_query_params)
            if flag:
                response = ResponseMessage.final_json("success", "Data Saved Successfully")

            logger.info("Completed excel_conf_name_insrt")
            return response
        except Exception as e:
            logger.exception("Error in excel_conf_name_insrt: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def fetch_excel_conf(self):
        try:
            logger.info("Inside fetch_excel_conf")
            resp = ResponseMessage.final_json("failed", "Unable to ge the Data", [])
            """fu1.name as createdBy, join {self.tables.frm_users} fu1 on 
                        fec.created_by = fu1.user_id"""
            query = f"""select fec.id as id, fec.name as name,  
                        DATE_FORMAT(fec.created_date, '%b %e, %Y %r') as createdDate,
                        DATE_FORMAT(fec.last_modified_date, '%b %e, %Y %r') as lastModifiedDate,
                        fu2.name as lastModifiedBy, case when fec.config is null then false else true end as config 
                        from {self.tables.frm_excel_configurations} fec join {self.tables.frm_users} fu2 on
                        fec.last_modified_by = fu2.user_id order by fec.last_modified_date desc"""
            flag, data = self.db_conn.select_mysql_table(query)
            if flag:
                resp = ResponseMessage.final_json("success", "Data Fetched Successfully", data)

            logger.info("Completed fetch_excel_conf")
            return resp
        except Exception as e:
            logger.exception("Error in fetch_excel_conf: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def delete_excel_config(self, db_id):
        try:
            logger.info("Inside delete_excel_config")
            query_statement_dict, query_dict = {}, {}
            query_statement_dict[
                "excel_conf_delete"] = f"""delete from {self.tables.frm_excel_configurations} where id = %s"""
            query_dict["excel_conf_delete"] = (db_id,)

            flag = self.db_conn.execute_query_transactions(query_statement_dict, query_dict)

            if flag:
                logger.info("Completed delete_excel_config")
                return {"status": "success", "message": "Data Deleted Successfully"}
            else:
                return {"status": "failed", "message": "Unable to Delete"}
        except Exception as e:
            logger.exception("Error in delete_excel_config: %s", str(e))
