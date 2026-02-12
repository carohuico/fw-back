from datetime import datetime
from fastapi import HTTPException
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
from scripts.constants import app_constants
from scripts.utils.sql_db_utils import DBUtility

db_utility = DBUtility()
app_constants_obj = app_constants.HomePage()
comm_utils_obj = CommonUtils()


class HomeHandler:
    def __init__(self):
        self.db_conn = DBUtility()
        self.table_id_prefix = app_constants.TableIdPrefix()
        self.tables = app_constants.TableName()

    def get_user_id(self, user):
        try:
            user_id_query = f""" Select user_id from {self.tables.frm_users} where username = %s"""
            flag, user_id_data = db_utility.select_mysql_fetchone(user_id_query, (user,))

            user_id = user_id_data.get("user_id", "") if user_id_data else ''
            return user_id
        except Exception as e:
            logger.error("Error in get_user_id: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def fetch_development_formulae(self, username, formula_type):
        """
            This method fetches the formulae from the db
            :param formula_type: Type of the formula that needs to be fetched
        """
        try:
            logger.info("Inside fetch_development_formulae")
            response = app_constants_obj.development_formulae_response
            body_content_data = list()
            user_id = self.get_user_id(username)

            if not user_id:
                return {"status": "failed", "message": "Invalid User", "data": body_content_data}
            if formula_type.lower() in ['draft', 'archived', 'synced']:
                formula_type = formula_type.title()
            else:
                formula_type = 'Draft'

            # Get the other table dummy data and create the correct query
            # new_query = f""" SELECT * FROM {self.tables.frm_formula} ff INNER JOIN {self.tables.frm_formula_attributes} ffa
            # ON ff.id = FFA.fk_formula AND FFA.attribute = 'CurrentStatus' AND FFA.value = %s order by ff.last_modified_date desc"""

            # Note: Uncomment this after development completion
            new_query = f""" 
            SELECT id, name, DATE_FORMAT(ff.created_date, '%b %e, %Y %r') as createdOn, DATE_FORMAT(ff.last_modified_date, '%b %e, %Y %r') as modifiedOn 
            FROM {self.tables.frm_formula} ff INNER JOIN {self.tables.frm_formula_attributes} ffa ON ff.ID = FFA.FK_FORMULA 
            AND FFA.ATTRIBUTE = 'CurrentStatus' AND FFA.VALUE = '{formula_type}' and created_by = '{user_id}' order by ff.last_modified_date desc
            """
            # query_params = (formula_type, user_id)
            flag, data = self.db_conn.select_mysql_table(new_query)
            if flag:
                response.update({"status": "success", "message": "Successfully loaded Development Formulas",
                                 "data": data})
            else:
                response.update({"status": "failed", "message": "No tables loaded", "data": body_content_data})

            logger.info("Fetching development formulas completed")
            return response
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def fetch_formula_comparison_projects(self, username):
        """
            This method fetches the formulae comparison projects from the db
        """
        logger.debug("Inside Fetch Formula Comparison Projects")
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return {"status": "failed", "message": "Invalid User"}
            response = app_constants_obj.comparison_projects_response
            
            # api_query = f""" SELECT ID as id, NAME as name, CREATEDDATE as createdOn, LASTMODIFIEDDATE as modifiedOn, 'delete' as action FROM {self.tables.frm_comp_project} order by LASTMODIFIEDDATE desc"""
            api_query = f""" SELECT id, name, DATE_FORMAT(createddate, '%b %e, %Y %r') as createdOn, DATE_FORMAT(lastmodifieddate, '%b %e, %Y %r') as modifiedOn, 'delete' as action FROM {self.tables.frm_comp_project} where author = '{user_id}' order by lastmodifieddate desc"""
            flag, data = self.db_conn.select_mysql_table(api_query)

            if flag:
                response.update({"status": "success", "message": "Successfully loaded Comparison Formulas",
                                 "data": data})
            else:
                response.update({"status": "failed", "message": "No tables loaded", "data": list()})

            logger.info("Completed fetch_formula_comparison_projects")
            return response
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def fetch_shared_formulae(self, username):
        try:
            logger.info("Inside fetch_shared_formulae")
            user_id_query = f"""
                SELECT f.id, f.name, f.created_date as createdOn, f.last_modified_date as modifiedOn
                FROM {self.tables.frm_shared_users} su
                JOIN {self.tables.frm_formula} f ON su.formulaid = f.id
                JOIN {self.tables.frm_users} u ON su.user_id = u.user_id
                WHERE u.username = %s order by f.last_modified_date desc
            """
            user_id_query_param = (username,)
            flag, data = self.db_conn.select_mysql_table(user_id_query, user_id_query_param)

            if not flag:
                raise HTTPException(status_code=500, detail="Failed to fetch shared formulas")

            response = {
                "status": "success",
                "message": "Successfully loaded Shared Formulas",
                "data": data
            }

            logger.info("Completed fetch_shared_formulae")
            return response

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def pagination(self, paginate):
        """
        :param paginate:
        :return:
        """
        try:
            page_number = paginate.page_number if hasattr(paginate, 'page_number') else None
            size = paginate.page_size if hasattr(paginate, 'page_size') else None
            if page_number is not None and size is not None:
                if page_number == 0:
                    limit_condition = f" limit {size} "
                else:
                    limit_condition = f" limit {size} offset {page_number * size - size} "
            else:
                limit_condition = " "
            return page_number, size, limit_condition
        except Exception as e:
            status_message = "Failed to apply pagination", str(e)
            logger.exception(status_message)
            return False, str(e)

    def fetch_name_details(self, username, input_json):
        try:
            logger.info("Inside fetch_name_details")
            response = app_constants_obj.shared_formulae_response
            body_content_data = list()
            user_id = self.get_user_id(username)
            # page_number, size, limit_condition = self.pagination(input_json)

            ref_id = input_json.ref_id.lower()
            # name = input_json.name.lower()

            comp_data = "lower(ff.ref_id) = %s"
            # elif name:
            #     comp_data = f"lower(ff.name) = %s"

            query = f"""select ff.id, ff.name, ff.ref_id as refId, ff.created_date as createdOn, 
                            ff.last_modified_date as modifiedOn 
                            from {self.tables.frm_formula} ff INNER JOIN {self.tables.frm_formula_attributes} ffa 
                            ON ff.id = FFA.fk_formula and FFA.attribute = 'CurrentStatus'
                            AND lower(FFA.value) = %s
                            where {comp_data} and server_id is not null and ff.created_by = %s"""

            # query = query + limit_condition

            flag, data = db_utility.select_mysql_table(query, ('draft', ref_id.lower(), user_id))

            if flag:
                response.update({"status": "success", "message": "data fetched Successfully", "data": list(data)})

            else:
                response.update({"status": "failed", "message": "No tables loaded", "data": body_content_data})

            logger.info("Completed fetch_name_details")
            return response
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def delete_compairson_project(self, comp_id):
        """
            Delete comparison project 
        """
        try:
            logger.info("Inside delete_compairson_project")
            response = dict()
            queries_dict = {}
            query_statement_dict = app_constants.QueryStatements.query_statement_dict
            query = f"""select formula_id as formulaId from {self.tables.frm_comp_server_formulas} 
                        where project_id = %s """
            # final_flag = True
            flag, data = self.db_conn.select_mysql_table(query, (comp_id,))

            if not flag:
                logger.error(" Error while fetching the data. Unable to the server formulas from db")
                return {"status": "failed", "message": "Unable to delete the Project"}

            if data:
                formula_id = data[0].get("formulaId", '')
                self.formula_item_delete(formula_id, queries_dict)
                query_statement_dict["frm_cmp_srvr_del"] = f""" Delete from {self.tables.frm_comp_server_formulas} where project_id = %s """
                queries_dict["frm_cmp_srvr_del"] = [(comp_id,)]

            query_statement_dict["frm_comp_prjct_del"] = f""" Delete from {self.tables.frm_comp_project} where id = %s """
            query_statement_dict["frm_cmp_lcl_frm_del"] = f""" Delete from {self.tables.frm_comp_local_formulas} where project_id = %s """
            queries_dict["frm_comp_prjct_del"] = [(comp_id,)]
            queries_dict["frm_cmp_lcl_frm_del"] = [(comp_id,)]
            del_flag = self.db_conn.execute_query_transactions(query_statement_dict,queries_dict)
            if del_flag:
                response.update({"status": "success", "message": "Comparison project deleted successfully"})
            else:
                response.update({"status": "failed", "message": "Failed to delete the Comparison Project"})

            logger.info("Completed delete_compairson_project")
            return response
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def check_for_existing_formula(self, formula_name):
        try:
            formula_query = f""" Select * from {self.tables.frm_formula} where name = '{formula_name}' """
            flag, data = self.db_conn.select_mysql_fetchone(formula_query)

            if data:
                return True
            else:
                return False

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def create_formula(self, formula_name, input_data, username):
        """
        Creates a formula
        :param formula_name: Formula name
        :param input_data: Formula data 
        """
        logger.debug("Inside Create Formula")
        try:
            response = {"status": "failed", "message": " Unable to create Formula !!! "}

            formula_item_name = input_data.get("name", "")
            ref_id = input_data.get("refId", "")
            class_type = input_data.get("classType", "")
            scrap_factor = input_data.get("scrapFactor", "")
            attributes = input_data.get("attributes", {})
            available_uom = input_data.get("availableUOMs", {})
            is_editable = False
            revision_code = input_data.get("revisionCode", "")
            revision_id = input_data.get("revisionId", "")
            org_id = input_data.get("orgId", "")
            item_id = input_data.get("itemId", "")
            bom_id = input_data.get("bomId", "")
            bom_type = input_data.get("bomType", "")

            # Get user details
            user_query = f""" Select * from {self.tables.frm_users} where username = %s """
            user_query_params = (username,)
            flag, user_data = self.db_conn.select_mysql_fetchone(user_query, user_query_params)

            created_by = user_data.get("user_id", "")
            last_mod_by = user_data.get("user_id", "")

            # current_timestamp_str = comm_utils_obj.time_stamp_generation
            current_timestamp_str = f'{datetime.now()}'

            # Check if the formula with the given name already exists
            if not self.check_for_existing_formula(formula_name):

                # Initialize IDs
                formula_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_formula)
                formula_item_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_formula_item)
                uom_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_uom)

                # For FRM_FORMULA_ITEM
                frm_formula_item_insert_query = f""" Insert INTO {self.tables.frm_formula_item}
                (id, name, fk_formula, quantity, fk_uom, pct_scrap_factor, is_deleted, material_ref, item_type, pct_composition, ref_id, 
                fk_produced_by_formula, sequence_number, food_contact, class_type, fk_selected_uom, item_id, org_id, revision_id, 
                revision_code, created_date, created_by, last_modified_date, last_modified_by) 
                values 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                frm_formula_item_data = (
                    formula_item_id, formula_item_name, None, 1, "", scrap_factor, 0, "", "output", 0, ref_id, formula_id, 0, "", class_type, uom_id, item_id, org_id, revision_id,
                    revision_code, current_timestamp_str, created_by, current_timestamp_str, last_mod_by)

                # For FRM_FORMULA
                frm_formula_insert_query = f""" Insert INTO {self.tables.frm_formula}
                (id, name, created_date, created_by, fk_formula_item_output, ref_id, last_modified_date, server_id, is_editable, 
                revision_code, revision_id, item_id, org_id, bom_id, bom_type, last_modified_by) 
                values 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                frm_formula_data = (
                    formula_id, formula_name, current_timestamp_str, created_by, formula_item_id, ref_id, current_timestamp_str, ref_id, 
                    is_editable, revision_code, revision_id, item_id, org_id, bom_id, bom_type, last_mod_by)

                # For FRM_ATTRIBUTE_DEF and FRM_FITEM_ATTR_VAL
                frm_attr_def_ids = dict()
                frm_fitem_attr_val_ids = dict()
                frm_attr_def_data = list()
                frm_fitem_attr_val_data = list()

                for attr_key, attr_val in attributes.items():
                    frm_attr_def_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_attribute_def)
                    frm_fitem_attr_val_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_fitem_attr_val)

                    frm_attr_def_ids.update(
                        {attr_key: comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_attribute_def)})
                    frm_fitem_attr_val_ids.update(
                        {attr_key: comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_fitem_attr_val)})

                    frm_attr_def_row = (frm_attr_def_id, attr_key, 'String', "", "", "", 0, 0, 1, 1, "")
                    frm_fitem_attr_val_row = (
                        frm_fitem_attr_val_id, 0, attr_val, 0, formula_item_id, frm_attr_def_id, "")

                    frm_attr_def_data.append(frm_attr_def_row)
                    frm_fitem_attr_val_data.append(frm_fitem_attr_val_row)

                frm_attr_def_insert_query = f""" Insert INTO {self.tables.frm_attribute_def}
                (id, name, type, rollup_type, src_sys_type, src_sys_id, ui_width, ui_hide_default, ui_editable, is_enabled, fk_attr_def_group) 
                values 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
                frm_fitem_attr_val_insert_query = f""" Insert INTO {self.tables.frm_fitem_attr_val}
                (id, value_measure, value_string, value_bool, fk_formula_item, fk_attribute_def, fk_uom) 
                values 
                (%s, %s, %s, %s, %s, %s, %s) """

                # For FRM_FORMULA_ATTRIBUTES
                frm_formula_attributes_data = [(formula_id, 'org', '000'), (formula_id, 'CurrentStatus', 'Draft')]
                frm_formula_attributes_query = f""" Insert INTO {self.tables.frm_formula_attributes}
                (fk_formula, attribute, value) 
                values 
                (%s, %s, %s) """

                # For FRM_UOM
                frm_uom_data = list()
                frm_uom_ids_list = list()

                for uom_key in available_uom.keys():
                    frm_uom_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_uom)

                    frm_uom_row = (frm_uom_id, uom_key, uom_key, 0, 0, 'unknown')
                    frm_uom_data.append(frm_uom_row)
                    frm_uom_ids_list.append(frm_uom_id)

                frm_uom_query = f""" Insert INTO {self.tables.frm_uom}
                (id, name, abbreviation, base_uom, conversion, category) 
                values 
                (%s, %s, %s, %s, %s, %s) """

                # For FRM_FITEM_ALT_UOM
                frm_fitem_alt_uom_data = list()

                for uom_id in frm_uom_ids_list:
                    frm_fitem_alt_uom_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_fitem_alt_uom)
                    frm_fitem_alt_uom_row = (frm_fitem_alt_uom_id, formula_item_id, uom_id, 1)

                    frm_fitem_alt_uom_data.append(frm_fitem_alt_uom_row)

                frm_fitem_alt_uom_query = f""" Insert INTO {self.tables.frm_fitem_alt_uom}
                (id, fk_formula_item, fk_alternate_uom, factor) 
                values 
                (%s, %s, %s, %s) """

                # Insert generated data
                self.db_conn.insert_mysql_table(frm_formula_item_insert_query, frm_formula_item_data)
                self.db_conn.insert_many_mysql_table(frm_fitem_alt_uom_query, frm_fitem_alt_uom_data)
                self.db_conn.insert_many_mysql_table(frm_uom_query, frm_uom_data)
                self.db_conn.insert_many_mysql_table(frm_formula_attributes_query, frm_formula_attributes_data)
                self.db_conn.insert_many_mysql_table(frm_attr_def_insert_query, frm_attr_def_data)
                self.db_conn.insert_many_mysql_table(frm_fitem_attr_val_insert_query, frm_fitem_attr_val_data)
                self.db_conn.insert_mysql_table(frm_formula_insert_query, frm_formula_data)

                response.update(
                    {"status": "success", "message": f" Formula {formula_name} created ! ", "data": formula_id})

            else:
                response.update(
                    {"status": "failed", "message": f" Formula with the name {formula_name} already exists ! ",
                     "data": ""})

            logger.info("Completed Formula Creation")
            return response
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def query_executor(self, query):
        try:

            flag, data = db_utility.select_mysql_table(query)

            if flag:
                return data

            else:
                return dict()

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def uom_delete(self, formula_item_id, queries_dict):
        try:
            query = f"""select fk_formula_item, fk_alternate_uom from {self.tables.frm_fitem_alt_uom} 
                        where fk_formula_item = '{formula_item_id}'"""
            data = self.query_executor(query)
            if data:
                frm_fitem_alt_uom_lst = queries_dict.get("frm_fitem_alt_uom_delete", [])
                frm_fitem_alt_uom_lst.extend([formula_item_id])
                queries_dict['frm_fitem_alt_uom_delete'] = frm_fitem_alt_uom_lst

                frm_uom_lst = queries_dict.get("frm_uom_delete", [])
                frm_uom_lst.extend([rec.get("fk_alternate_uom", '') for rec in data])
                queries_dict['frm_uom_delete'] = frm_uom_lst

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def attributes_delete(self, formula_item_id, queries_dict):
        try:
            query = f"""select id, fk_formula_item, fk_attribute_def from {self.tables.frm_fitem_attr_val} 
                        where fk_formula_item = '{formula_item_id}'"""
            data = self.query_executor(query)
            if data:
                frm_fitem_attr_val_lst = queries_dict.get("frm_fitem_attr_val_delete", [])
                frm_fitem_attr_val_lst.extend([(formula_item_id,)])
                queries_dict['frm_fitem_attr_val_delete'] = frm_fitem_attr_val_lst

                frm_attribute_def_lst = queries_dict.get("frm_attribute_def_delete", [])
                frm_data = [rec.get("fk_attribute_def", '') for rec in data
                            if rec.get("id", '') not in frm_attribute_def_lst]
                frm_attribute_def_lst.extend(frm_data)
                queries_dict['frm_attribute_def_delete'] = frm_attribute_def_lst

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_delete(self, db_id, queries_dict, after_sync=True):
        try:
            if after_sync:
                frm_formula_lst = queries_dict.get("frm_formula_delete", [])
                frm_formula_lst.extend([(db_id,)])
                queries_dict['frm_formula_delete'] = frm_formula_lst

                frm_formula_attributes_lst = queries_dict.get("frm_formula_attributes_delete", [])
                frm_formula_attributes_lst.extend([(db_id,)])
                queries_dict['frm_formula_attributes_delete'] = frm_formula_attributes_lst

            query = f"""select id, fk_produced_by_formula from {self.tables.frm_formula_item} 
                        where fk_formula = '{db_id}'"""
            data = self.query_executor(query)

            if data:
                for rec in data:
                    fi_id = rec.get("id", '')
                    if fi_id:
                        self.formula_item_delete(fi_id, queries_dict, 'id')

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_item_delete(self, db_id, queries_dict, col_name='fk_produced_by_formula'):
        try:
            query = f"""select id, fk_produced_by_formula from {self.tables.frm_formula_item} where {col_name} = '{db_id}'"""

            data = self.query_executor(query)

            if data:
                data = data[0]
                frm_formula_item_id = data.get("id")
                frm_formula_item_delete_data = queries_dict.get("frm_formula_item_delete", [])
                frm_formula_item_delete_data.extend([(frm_formula_item_id,)])
                queries_dict['frm_formula_item_delete'] = frm_formula_item_delete_data

                self.uom_delete(frm_formula_item_id, queries_dict)
                self.attributes_delete(frm_formula_item_id, queries_dict)
                if data.get("fk_produced_by_formula", None):
                    self.formula_delete(data.get("fk_produced_by_formula", None), queries_dict)

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def delete_development_formulae(self, formula_id):
        """
            This method fetches the formulae from the db    
            :param formula_id: The formula that needs to be fetched
        """
        logger.debug("Inside Delete Development Formulae")
        try:
            queries_dict = {}
            query_statement_dict = app_constants.QueryStatements.query_statement_dict
            response = app_constants.ResponseMessage.final_json("failed", "unable to Delete the Formula")
            self.formula_item_delete(formula_id, queries_dict)

            if queries_dict:
                flag = db_utility.execute_query_transactions(query_statement_dict, queries_dict)
                if flag:
                    response = app_constants.ResponseMessage.final_json("success", "Formula Deleted Successfully")

            return response
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def children_deletion_after_sync(self, db_id):
        try:
            queries_dict = dict()
            self.formula_delete(db_id, queries_dict, after_sync=False)

            return queries_dict

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def update_formula_status_handler(self, formula_id, formula_status):
        try:
            logger.info("Inside update_formula_status_handler")
            response = app_constants.ResponseMessage.final_json("failed", "Unable to Update the Formula Status",[])
            if formula_status.lower() not in ['draft', 'archived', 'synced']:
                return response
            
            formula_status_val = formula_status.title()

            # Deletion of archived formula
            if formula_status_val in ['Archived']:
                # Check if the formula is being used in any comparison project
                frm_comp_check_qry = f""" Select fcp.id, fcp.baseformulaid, fcp.isbaseformulalocal, fclf.project_id from {self.tables.frm_comp_project} fcp inner join {self.tables.frm_comp_local_formulas} fclf on fcp.id = fclf.project_id 
                where fclf.formula_id = %s ;"""
                frm_comp_check_flag, frm_comp_check_data = self.db_conn.select_mysql_table(frm_comp_check_qry, (formula_id,))

                # If data exists, get all the comparison formulas related to it
                if frm_comp_check_data:

                    for fcp_data in frm_comp_check_data:
                        # Check if the formula is a base formula and add a new base formula if it is
                        project_id = fcp_data.get("id", "")
                        if fcp_data.get("baseformulaid", "") == formula_id:
                            # Find an alternative formula to make as baseformula
                            bfrm_query = f"""Select * from {self.tables.frm_comp_local_formulas} where formula_id <> '{formula_id}' and project_id = '{project_id}'"""
                            bfrm_flag, bfrm_data = self.db_conn.select_mysql_table(bfrm_query)

                            new_bfrm_id = bfrm_data[0].get('formula_id', '')
                            bfrm_attr_query = f""" Select * from {self.tables.frm_formula_attributes} where fk_formula = '{new_bfrm_id}' and lower(attribute) = 'currentstatus' """
                            bfrm_attr_flag, bfrm_attr_data = self.db_conn.select_mysql_table(bfrm_attr_query)

                            if bfrm_attr_data[0].get('value', '').lower() == 'plmcomparison':
                                is_bfrm_local = 0
                            else:
                                is_bfrm_local = 1

                            # update new bfrm id in the comp project table 
                            bfrm_upd_query = f"""update {self.tables.frm_comp_project} set baseformulaid = '{new_bfrm_id}', isbaseformulalocal = {is_bfrm_local}
                            where id = '{project_id}' """
                            bfrm_upd_flag = self.db_conn.update_mysql_table(bfrm_upd_query)

                        # Delete the formula being archived from local comp projects
                        del_qry = f""" Delete from {self.tables.frm_comp_local_formulas} where project_id = '{project_id}' and formula_id = '{formula_id}'"""
                        self.db_conn.delete_mysql_table(del_qry)

                query = f"""update {self.tables.frm_formula_attributes} set value = %s 
                            where fk_formula = %s and lower(attribute) = 'currentstatus' """
                query_params = (formula_status_val, formula_id)

                flag = db_utility.update_mysql_table(query, query_params)
                if flag:
                    response = app_constants.ResponseMessage.final_json("success", "Formula Status Updated Successfully", [])                    

            else:
                query = f"""update {self.tables.frm_formula_attributes} set value = %s 
                            where fk_formula = %s and lower(attribute) = 'currentstatus' """
                query_params = (formula_status_val, formula_id)

                flag = db_utility.update_mysql_table(query, query_params)
                if flag:
                    response = app_constants.ResponseMessage.final_json("success", "Formula Status Updated Successfully", [])

            logger.info("Completed update_formula_status_handler")
            return response
        except Exception as e:
            logger.exception("Error in update_formula_status_handler %s", e)
            raise HTTPException(status_code=401, detail=e.args, ) from e
