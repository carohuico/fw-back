from fastapi import HTTPException
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
from concurrent.futures import ThreadPoolExecutor, as_completed
from scripts.constants.app_constants import TableName, ResponseMessage
from scripts.core.handlers.formula_handlers import FormulaHandler
from scripts.core.handlers.formula_handlers import HomeHandler
from scripts.utils.sql_db_utils import DBUtility
from scripts.constants import app_constants
from datetime import datetime
from scripts.constants.app_constants import FormulaComparisonConstants

comm_utils_obj = CommonUtils()
formula_handler_obj = FormulaHandler()
home_handler_obj = HomeHandler()

class FormulaComparisonHandler:

    def __init__(self):
        self.db_conn = DBUtility()
        self.table_id_prefix = app_constants.TableIdPrefix()
        self.tables = app_constants.TableName()

    def fcmp_data(self, project_id):
        try:
            query = f"""select fcp.id as dbId,fcp.name, fcp.author, fcp.createdDate, fcp.lastModifiedDate,
                        fcp.baseFormulaId, isBaseFormulaLocal, clf.formula_id, fsf.project_id as fsf_pid, 
                        fsf.formula_id as fsf_fid from {self.tables.frm_comp_project} fcp 
                        left join {self.tables.frm_comp_local_formulas} clf on 
                        fcp.id = clf.project_id left join {self.tables.frm_comp_server_formulas} 
                        fsf on fcp.id = fsf.project_id where fcp.id = '{project_id}'"""

            flag, data = self.db_conn.select_mysql_table(query)
            return data if flag else []
        except Exception as e:
            logger.error("Error in formula_data %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def get_formula_comparison_projects(self,username, project_id):
        try:
            logger.info("Inside fetching formula comparison project tree")
            main_data = dict()
            response = ResponseMessage.final_json("Failed", "Unable to fetch the Comparison Projects", main_data)

            data = self.fcmp_data(project_id)
            result = []
            lst_dict = {}
            server_frm_data = []

            if data:
                main_data['headerChildren'] = FormulaComparisonConstants.header_children
                keys_pop = ['formula_id', 'fsf_pid', 'fsf_fid']
                main_data.update(data[0])
                local_frm = list()
                # sr_id = data[0].get('fsf_fid', None)
                server_frm = []

                for rec in data:
                    frm_id = rec.get('formula_id', None)
                    if frm_id and frm_id not in local_frm:
                        local_frm.append(frm_id)

                    fsf_id = rec.get('fsf_fid', None)
                    if fsf_id and fsf_id not in server_frm:
                        server_frm.append(fsf_id)

                [main_data.pop(key) for key in keys_pop]

                if local_frm:
                    with ThreadPoolExecutor(max_workers=FormulaComparisonConstants.workers_count) as executor:
                        futures = [executor.submit(formula_handler_obj.get_formula_details_service, db_id) for db_id in
                                   local_frm]

                    for res in as_completed(futures):
                        res_data = res.result().get("data", [])
                        if res_data:
                            lst_dict[res_data[0].get("formula", {}).get("dbId", '')] = res_data
                    for rec in local_frm:
                        result.extend(lst_dict.get(rec))

                main_data['localFormulaTrees'] = result

                if server_frm:
                    srvr_data = {}
                    with ThreadPoolExecutor(max_workers=FormulaComparisonConstants.workers_count) as executor:
                        futures = [executor.submit(formula_handler_obj.get_formula_details_service, db_id) for db_id in
                                   server_frm]

                    for res in as_completed(futures):
                        res_data = res.result().get("data", [])
                        if res_data:
                            srvr_data[res_data[0].get("formula", {}).get("dbId", '')] = res_data
                    
                    # For getting the formulas in the correct order
                    srvr_form_ids_query = f""" Select formula_id from {self.tables.frm_comp_server_formulas} where project_id = %s """
                    srvr_form_ids_params = (project_id,)
                    srvr_form_flag, srvr_form_data = self.db_conn.select_mysql_table(srvr_form_ids_query, srvr_form_ids_params)

                    for rec in srvr_form_data:
                        server_frm_data.extend(srvr_data.get(rec.get("formula_id", "")))

                    # server_frm_data = formula_handler_obj.get_formula_details_service(server_frm[0])
                    # server_frm_data = plm_handler_obj.get_server_formula_tree(username, server_frm[0], bom='primary', org='000',
                    #                         input_payload={"type": "comparisonTree"})
                    # server_data = server_frm_data
                    server_frm = [rec.get("formula", {}).get("name", '') for rec in server_frm_data]

                main_data['serverFormulas'] = server_frm
                main_data['serverFormulaTrees'] = server_frm_data

                response = ResponseMessage.final_json("success", "Data Fetched Successfully", [main_data])

            logger.info("Completed fetching formula comparison project tree")
            return response
        except Exception as e:
            logger.error("Error in get_formula_comparison_projects %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def chld_comp(self, chld_data, base_formula_id):
        try:
            base_data = chld_data.get(base_formula_id, '')
            id_list = []
            for key, value in chld_data.items():
                if key == base_formula_id:
                    continue
                if value == base_data:
                    id_list.append(key)

            return id_list
        except Exception as e:
            logger.error("Error in chld_comp %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def query_condition(self, data_list, query, opt_cond=''):
        try:
            db_list_len = len(data_list)
            query_execution = True
            if db_list_len == 0:
                query_execution = False
            elif db_list_len == 1:
                query = query + f"""{'<>' if opt_cond else '='} '{tuple(data_list)[0]}'"""
            else:
                query = query + f"""{opt_cond} in {tuple(data_list)}"""

            return query_execution, query
        except Exception as e:
            logger.error("Error in query_conditions %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def att_json(self, query_data, frm_data, base_formula_id, existing_prjct_ids):
        try:
            chld_data = {}
            data = []
            [chld_data.setdefault(item.get("fk_formula", ''), []).append(item.get("name", '')) for
             item in frm_data if
             'fk_formula' in item and 'name' in item]
            id_lst = self.chld_comp(chld_data, base_formula_id)
            att_query = f"""select fk_formula, attribute, value from {TableName.frm_formula_attributes} 
                                                                                                where fk_formula"""
            query_flag, query = self.query_condition(id_lst, att_query)
            if query_flag:
                flag, att_data = self.db_conn.select_mysql_table(query)
                att_dict = {}
                data = []
                if flag and att_data:
                    for rec in att_data:
                        att_name = rec.get('attribute', '')
                        att_value = rec.get('value', '')
                        fk_formula = rec.get('fk_formula', '')

                        if fk_formula not in att_dict:
                            att_dict[fk_formula] = dict()

                        att_dict[fk_formula][att_name] = att_value

                    for rec in query_data:
                        db_id = rec.get('dbId', '')
                        if db_id in existing_prjct_ids:
                            continue
                        if db_id in id_lst:
                            attribute_data = att_dict.get(db_id, {})
                            rec.update({"attributes": attribute_data})
                            data.append(rec)
            return data
        except Exception as e:
            logger.error("Error in %s", str(e))

    def attribute_data(self, query_data):
        try:
            db_id_list = [rec.get('dbId', '') for rec in query_data]
            att_query = f"""select fk_formula, attribute, value from {TableName.frm_formula_attributes} 
                                                    where fk_formula"""
            query_flag, query = self.query_condition(db_id_list, att_query)
            data = []
            if query_flag:
                exec_flg, att_data = self.db_conn.select_mysql_table(query)
                if exec_flg:
                    att_js = {}

                    for rec in att_data:
                        if rec['fk_formula'] not in att_js:
                            att_js[rec['fk_formula']] = {}
                        att_js[rec['fk_formula']][rec["attribute"]] = rec['value']

                    for rec in query_data:
                        rec["attributes"] = att_js.get(rec.get('dbId'), {})
                        data.append(rec)

            return data if data else query_data
        except Exception as e:
            logger.error("Error in attribute_data: %s", str(e))

    def search_local_formulas(self, user, ref_id, project_id):
        try:
            logger.info("Inside searching for local formulas")
            query_data = self.fcmp_data(project_id)
            resp = ResponseMessage.final_json("failed", "Unable to get the corresponding formulas", [])
            user_id = formula_handler_obj.get_user_id(user)

            if query_data:
                # existing_prjct_ids = [rec.get("formula_id", '') for rec in query_data]
                # base_formula_id = query_data[0].get('baseFormulaId', '')

                query = f"""select fm.id as dbId, fm.ref_id as refId, fm.name as name, 
                            DATE_FORMAT(fm.created_date, '%b %e, %Y %r') as createdDate,
                            DATE_FORMAT(fm.last_modified_date, '%b %e, %Y %r') as lastModifiedDate,
                            fm.server_id as serverId from {TableName.frm_formula}  fm 
                            join {TableName.frm_formula_item} fi 
                            on fm.id = fi.fk_produced_by_formula 
                            and fk_formula is null join {TableName.frm_formula_attributes} ffa on fm.id=ffa.fk_formula and
                            FFA.attribute = 'CurrentStatus' and ffa.value not in ('PLMComparison', 'Archived') where fm.ref_id = '{ref_id}' and fm.created_by = '{user_id}' """

                # query_flag, query = self.query_condition(existing_prjct_ids, query, 'not')

                if True:
                    flag, query_data = self.db_conn.select_mysql_table(query)
                    if flag:
                        if query_data:
                            main_data = self.attribute_data(query_data)
                            resp = ResponseMessage.final_json("success", "Data Fetched Successfully", main_data)
                        else:
                            resp = ResponseMessage.final_json("success", "No Formulas to show", [])

                        # db_id_list.append(base_formula_id)
                        # if db_id_list:
                        #     query = f"""select name, fk_formula from {TableName.frm_formula_item}
                        #                 where fk_formula """
                        #     query_flag, query = self.query_condition(db_id_list, query)
                        #     if query_flag:
                        #         query = query + " order by fk_formula, sequence_number"
                        #         flag, chld_data = self.db_conn.select_mysql_table(query)
                        #         if flag and chld_data:
                        #             data = self.att_json(query_data, chld_data, base_formula_id, existing_prjct_ids)
                        #
                        #             resp = ResponseMessage.final_json("success", "Data Fetched SuccessFully", data)
            logger.info("Completed search for local formulas")
            return resp
        except Exception as e:
            logger.error("Error in search_local_formulas: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def create_formula_comparison_project(self, username, formula_id, formula_name):
        try:
            logger.info("Inside creation of formula comparison project")
            # Initialize data
            current_timestamp_str = f'{datetime.now()}'
            comp_project_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_comp_project)

            # Get creator user id
            user_id_query = f""" Select user_id from {self.tables.frm_users} where username = '{username}' """
            user_flag, user_id_data = self.db_conn.select_mysql_fetchone(user_id_query)
            user_id = user_id_data.get("user_id", "")

            frm_dat_qry = f"""select name from {self.tables.frm_comp_project} where lower(name) = %s"""
            frm_flag, name_data = self.db_conn.select_mysql_fetchone(frm_dat_qry, (formula_name.lower(),))
            if name_data:
                return {"status": "failed", "message": "Project Name Already Exists"}

            create_query_one = f""" Insert into {self.tables.frm_comp_project} 
            (ID, NAME, AUTHOR, CREATEDDATE, LASTMODIFIEDDATE, BASEFORMULAID, ISBASEFORMULALOCAL) 
            values 
            (%s, %s, %s, %s, %s, %s, %s) """
            create_query_one_data = (comp_project_id, formula_name, user_id, current_timestamp_str, current_timestamp_str, formula_id, True)

            create_query_two = f""" Insert into {self.tables.frm_comp_local_formulas} 
            (PROJECT_ID, FORMULA_ID) 
            values
            (%s, %s) """
            create_query_two_data = (comp_project_id, formula_id)

            creation_one_flag = self.db_conn.insert_mysql_table(create_query_one, create_query_one_data)
            creation_two_flag = self.db_conn.insert_mysql_table(create_query_two, create_query_two_data)

            if creation_one_flag and creation_two_flag:
                status = "success"
                message = "Comparison Project created successfully"
                data = comp_project_id
            else:
                status = "failed"
                message = "Failed to create comparison Project"
                data = ""

            logger.info("Completed creation of formula comparison project")
            return {"status": status, "message": message, "data": data}
        except Exception as e:
            logger.error("Error in create_formula_comparison_project %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def save_comparison_project(self, username, input_json):
        try:
            logger.info("Inside save changes in comparison project")
            comp_project_id = input_json.get("dbId", "")
            local_project_ids = input_json.get("localDbIds", [])
            user_id = formula_handler_obj.get_user_id(username)
            # project_name = input_json.get("name", "")
            base_formula_id = input_json.get("baseFormulaId", "")
            srvr_frm_tree = input_json.get("serverFormulaTrees", [])
            is_base_local_frm = input_json.get("isBaseFormulaLocal", True)
            server_id_lst = input_json.get("serverIds", [])
            current_timestamp_str = datetime.now()
            frm_id_lst = []

            exs_server_query = f"""select formula_id from {self.tables.frm_comp_server_formulas} where project_id = '{comp_project_id}'"""
            flag, exs_srvr_lst = self.db_conn.select_mysql_table(exs_server_query)
            if not flag:
                return {"status": "failed", "message": f"Unable to save project !!"}
            # exs_srvr_lst = exs_server_id[0].get("formula_id", None) if exs_server_id else []
            query_statements_dict = formula_handler_obj.queries_statement_dict()
            queries_dict = {}
            if exs_srvr_lst:
                query_statements_dict['server_frm_del'] = f""" delete from {self.tables.frm_comp_server_formulas} where project_id = %s """
                queries_dict['server_frm_del'] = (comp_project_id,)
            if server_id_lst:
                if not srvr_frm_tree:
                    return {"status": "failed", "message": "Unable to get the Server Tree"}
                for frm_json in srvr_frm_tree:
                    # if not frm_json:
                    #     return {"status": "failed", "message": "Server Tree data is empty"}
                    formula_id = frm_json.get("formula", {}).get("dbId", '')
                    if not formula_id:
                        frm_json.get("formula", {}).get("attributes", {}).update({"currentStatus": "PLMComparison"})

                        formula_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_formula)
                        formula_handler_obj.formula_chld_insertion(user_id, formula_id, frm_json, queries_dict,
                                                          seq_num=frm_json.get("sequenceNumber", 0), frm_name=frm_json.get("formula", {}).get("name", ''))
                    frm_id_lst.append(formula_id)
                query_statements_dict['server_frm_ins'] = f"""insert into {self.tables.frm_comp_server_formulas} 
                                                                                (project_id, formula_id) values (%(project_id)s, %(formula_id)s) """

                queries_dict['server_frm_ins'] = [{"project_id": comp_project_id, "formula_id": rec} for rec in
                                                      frm_id_lst]

            for rec in exs_srvr_lst:
                formula_id = rec.get("formula_id", None)
                if formula_id in frm_id_lst or not formula_id:
                    continue
                home_handler_obj.formula_item_delete(formula_id, queries_dict)


            # Delete existing local formulas set
            query_statements_dict['local_frm_del'] = f""" Delete FROM {self.tables.frm_comp_local_formulas} where PROJECT_ID = %s """
            queries_dict['local_frm_del'] = (comp_project_id,)
            query_statements_dict['local_frm_ins'] = f""" Insert INTO {self.tables.frm_comp_local_formulas} (project_id, formula_id) values (%s, %s) """
            query_statements_dict['upd_frm_cmp_prjct'] = f""" Update {self.tables.frm_comp_project} set baseformulaid = %(baseformulaid)s,isbaseformulalocal = %(isbaseformulalocal)s, lastmodifieddate = %(lastmodifieddate)s where id = %(id)s """
            queries_dict['upd_frm_cmp_prjct'] = [{"baseformulaid":base_formula_id, "isbaseformulalocal":is_base_local_frm, "lastmodifieddate":current_timestamp_str, "id":comp_project_id}]

            insertion_data = list()

            for lcp_id in local_project_ids:
                insertion_data.append((comp_project_id, lcp_id))
            queries_dict['local_frm_ins'] = insertion_data
            flag = self.db_conn.execute_query_transactions(query_statements_dict,queries_dict)

            logger.info("Completed save changes in comparison project")
            if flag:
                return {"status": "success", "message": f" Project saved successfully !!"}
            else:
                return {"status": "failed", "message": f"Unable to save project !!"}
        except Exception as e:
            logger.error("Error in save_comparison_project %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def save_as_comparison_project(self, username, input_json):
        try:
            logger.info("Inside creation of a copy of comparison project formula")
            query_statements_dict = formula_handler_obj.queries_statement_dict()
            queries_dict = {}
            data = {}
            # Initialize data
            current_timestamp_str = f'{datetime.now()}'
            comp_project_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_comp_project)
            formula_name = input_json.get("name", "")
            local_project_ids = input_json.get("localDbIds", [])
            base_formula_id = input_json.get("baseFormulaId", "")
            srvr_frm_tree = input_json.get("serverFormulaTrees", [])
            server_id_lst = input_json.get("serverIds", [])
            base_local_frm_flag = input_json.get("isBaseFormulaLocal", True)
            # Check if comp project with the same name exists
            if not formula_name:
                return {"status": "failed", "message": "Formula comparison project name is empty"}
            comp_proj_query = f""" Select * from {self.tables.frm_comp_project} where NAME = '{formula_name}' """
            comp_proj_flag, comp_proj_data = self.db_conn.select_mysql_fetchone(comp_proj_query)
            if comp_proj_data:
                return {"status": "failed", "message": f"A comparison project with the name {formula_name} already exists "}

            # Get creator user id
            user_id_query = f""" Select user_id from {self.tables.frm_users} where username = '{username}' """
            user_flag, user_id_data = self.db_conn.select_mysql_fetchone(user_id_query)
            user_id = user_id_data.get("user_id", "")

            query_statements_dict['create_query_one'] = f""" Insert into {self.tables.frm_comp_project} 
            (id, name, author, createddate, lastmodifieddate, baseformulaid, isbaseformulalocal) 
            values 
            (%(id)s, %(name)s, %(author)s, %(createddate)s, %(lastmodifieddate)s, %(baseformulaid)s, %(isbaseformulalocal)s) """
            queries_dict['create_query_one'] = [{"id":comp_project_id, "name": formula_name, "author": user_id,
                                                 "createddate": current_timestamp_str, "lastmodifieddate": current_timestamp_str,
                                                 "baseformulaid": base_formula_id, "isbaseformulalocal": base_local_frm_flag}]

            query_statements_dict['create_query_two'] = f""" Insert into {self.tables.frm_comp_local_formulas} 
            (project_id, formula_id) 
            values
            (%s, %s) """
            create_query_two_data = list()

            for lcp_id in local_project_ids:
                create_query_two_data.append((comp_project_id, lcp_id))
            queries_dict['create_query_two'] = create_query_two_data
            query_statements_dict['create_query_three'] = f"""insert into {self.tables.frm_comp_server_formulas}(project_id, formula_id)
                                            values(%(project_id)s, %(formula_id)s)"""
            if server_id_lst:
                if not srvr_frm_tree:
                    return {"status": "failed", "message": "Unable to get the Server Tree"}
                frm_id_lst = []
                for frm_json in srvr_frm_tree:

                    # if not frm_json:
                    #     return {"status": "failed", "message": "Server Tree data is empty"}

                    frm_json.get("formula", {}).get("attributes", {}).update({"currentStatus": "PLMComparison"})

                    formula_id = comm_utils_obj.unique_id_generator(self.table_id_prefix.frm_formula)
                    formula_handler_obj.formula_chld_insertion(user_id, formula_id, frm_json, queries_dict,
                                                               seq_num=frm_json.get("sequenceNumber", 0),
                                                               frm_name=frm_json.get("formula", {}).get("name", ''))
                    frm_id_lst.append(formula_id)

                queries_dict['create_query_three'] = [{"project_id": comp_project_id, "formula_id": rec} for rec in frm_id_lst]

            flag = self.db_conn.execute_query_transactions(query_statements_dict, queries_dict)

            if flag:
                status = "success"
                message = "Comparison Project created successfully"
                data = {"project_id": comp_project_id, "name": formula_name}
            else:
                status = "failed"
                message = "Failed to create comparison Project"

            logger.info("Completed creation of a copy of comparison project formula")
            return {"status": status, "message": message, "data": data}
        except Exception as e:
            logger.error("Error in save_as_comparison_project %s", str(e))

    def get_configurations(self):
        try:
            data = {
                "decimalPrecision": FormulaComparisonConstants.decimal_precision,
                "formulaStatuses": ["Draft", "Archived", "Synced"],
                "availableBOMs": FormulaComparisonConstants.bomname_list
            }
            """user: user to be added"""
            return data
        except Exception as e:
            logger.error("Error in get_configurations: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e
