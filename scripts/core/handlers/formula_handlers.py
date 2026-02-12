from fastapi import HTTPException, Response
from datetime import datetime
import xlsxwriter as xlw
import uuid
import io
from fastapi.responses import StreamingResponse
import json
import re
from datetime import datetime
import pandas as pd

from scripts.core.handlers import table_config_handler
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils
from scripts.core.handlers.home_handler import HomeHandler
from scripts.constants.app_constants import TableName, TableIdPrefix, Attributes, ResponseMessage, QueryStatements, ChildrenConfigs
from scripts.utils.sql_db_utils import DBUtility

db_utility = DBUtility()
comm_utils_obj = CommonUtils()
table_config_obj = table_config_handler.TableConfig()


class FormulaHandler:

    def __init__(self):
        """
            to be initialised
        """
        self.db_conn = DBUtility()
        self.tables = TableName()
        self.table_id_prefix = TableIdPrefix()

    def uom_generator(self, data):
        try:

            rem_list = ['uom_name', 'category', 'factor']
            main_data = data[0] if data else dict()

            main_data['availableUOMs'] = {
                rec.get("baseUOM", ""): {'name': rec.get("uom_name", ""), 'category': rec.get("category", ""),
                                         'factor': rec.get("factor", 0)} for rec in data}
            [main_data.pop(key, None) for key in rem_list]
            return main_data

        except Exception as e:
            logger.error("error in uom_generator %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def attribute_generator(self, attribute_data):
        try:

            att_data = {att.get("name", ""): att.get("value", "") for att in attribute_data}

            return att_data

        except Exception as e:
            logger.error("error in attribute_generator %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def children_generator(self, children_id, chld_formula_id):
        try:
            children_dict = {}

            query = f"""select fi.id as dbId, fi.ref_id as refId, fi.name, fi.quantity, fi.pct_scrap_factor as 
                        scrapFactor,  fi.is_deleted as deleted, fi.pct_composition as percentage, fi.ITEM_TYPE as type, 
                        fi.class_type as classType, fi.SEQUENCE_NUMBER as sequenceNumber, fu.name as baseUOM, 
                        fu.name as selectedUOM, fu.name as uom_name, 
                        fu.category, fau.factor, fi.item_id as itemId, fi.org_id as orgId,
                        fi.revision_id as revisionId, fi.revision_code as revisionCode, 
                        DATE_FORMAT(fi.created_date, '%b %e, %Y %r') as createdDate,
                        fi.created_by as createdBy, DATE_FORMAT(fi.last_modified_date, '%b %e, %Y %r') 
                        as lastModifiedDate, fi.last_modified_by as lastModifiedBy, fi.substitute_parent substituteParent
                        from  {TableName.frm_formula_item} fi join {TableName.frm_fitem_alt_uom} fau 
                        on fi.id = fau.FK_FORMULA_ITEM join {TableName.frm_uom} fu on 
                        fau.fk_alternate_uom = fu.id  where fi.id = '{children_id}';"""
            flag, data = db_utility.select_mysql_table(query)

            if flag:

                main_children_data_dict = self.uom_generator(data)
                children_dict.update(main_children_data_dict)
                attribute_query = f"""select ad.Name as name,av.value_string as value from 
                                        {TableName.frm_fitem_attr_val} av 
                                      join {TableName.frm_attribute_def} ad on av.FK_ATTRIBUTE_DEF = ad.id where 
                                      av.FK_FORMULA_ITEM= '{children_id}'"""
                attribute_flag, attribute_data = db_utility.select_mysql_table(attribute_query)
                children_dict['substitutes'] = []
                if attribute_flag:
                    children_dict['attributes'] = self.attribute_generator(attribute_data)
                if chld_formula_id:
                    children_dict['formula'] = self.formula_generator(chld_formula_id)

            return children_dict
        except Exception as e:
            logger.exception("Error in children_generator: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def label_mockup_sheet(self, workbook, frm_data):
        try:
            frm_number = frm_data.get('refId', '')
            frm_name = frm_data.get("name", '')
            ws = workbook.add_worksheet("label_mockup")

            heading_format = {
                "bold": True,
                "font_size": 12,
                "font_name": 'Arial'
            }
            fmt = workbook.add_format(heading_format)
            ws.write('A1', "Formula Number", fmt)
            ws.set_column(0, 0, 35)
            ws.write('B1', frm_number)
            ws.write('A2', "Product Name", fmt)
            ws.write('B2', frm_name)
            ws.set_column(2, 0, 35)
        except Exception as e:
            logger.error("Error while creating label_Mockup Sheet %s", str(e))

    def substitute_generator(self, chld_lst):
        try:
            main_lst = []
            sub_js = {}
            for rec in chld_lst:
                if rec.get("substituteParent", None):
                    if rec["substituteParent"] not in sub_js:
                        sub_js[rec["substituteParent"]] = list()
                    sub_js[rec["substituteParent"]].append(rec)
                    continue
                main_lst.append(rec)

            """# sub_js = {rec.get("substituteParent", None): rec for rec in chld_lst if rec.get("substituteParent", None)}"""

            if not sub_js:
                return chld_lst

            sub_lst = []

            for rec in main_lst:
                item_id = rec.get("itemId", None)
                if item_id in sub_js:
                    rec["substitutes"].extend(sub_js[item_id])
                sub_lst.append(rec)
            return sub_lst if sub_lst else chld_lst

        except Exception as e:
            logger.exception("Error in substitute_generator: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_generator(self, formula_id):
        try:
            children_list = list()
            formula_tree_data = dict()
            formula_query = f"""select id as dbId, ref_id as refId, name, DATE_FORMAT(CREATED_DATE, '%b %e, %Y %r') 
                                as createdDate, 
                                DATE_FORMAT(LAST_MODIFIED_DATE, '%b %e, %Y %r') as lastModifiedDate, 
                                SERVER_ID as serverId,
                                is_editable as childrenEditable,bom_id as bomId, 
                                bom_type as bomType, last_modified_by as lastModifiedBy
                                from {TableName.frm_formula} where id = '{formula_id}' """

            formula_query_params = (formula_id,)
            formula_flag, formula_data = db_utility.select_mysql_table(formula_query)

            if formula_flag and len(formula_data) != 0:

                formula_tree_data = formula_data[0]

                formula_att_query = f"""select attribute as name,value from {TableName.frm_formula_attributes} 
                                        where fk_formula = %s """

                formula_attribute_flag, formula_attribute_data = db_utility.select_mysql_table(formula_att_query, formula_query_params)

                if formula_attribute_flag:

                    formula_tree_data['attributes'] = self.attribute_generator(formula_attribute_data)

                    list_of_children_query = f"""select id, fk_produced_by_formula from {TableName.frm_formula_item} 
                                                where fk_formula = %s order by sequence_number asc"""
                    children_flag, children_data = db_utility.select_mysql_table(list_of_children_query, formula_query_params)

                    if children_flag:
                        for chld in children_data:

                            chld_id = chld.get("id", None)
                            chld_formula_id = chld.get('fk_produced_by_formula', None)

                            if chld_id:
                                chld_data = self.children_generator(chld_id, chld_formula_id)

                                children_list.append(chld_data)

                        formula_tree_data['children'] = self.substitute_generator(children_list) if children_list else children_list

            return formula_tree_data

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def get_formula_details_service(self, formula_tree_id):
        try:
            logger.info("Inside Fetching formula tree JSON data")
            response = dict()
            body_content_data = list()
            main_dict = dict()
            query = f"""select fi.id as dbId, fi.ref_id as refId, fi.name, fi.quantity, fi.pct_scrap_factor as 
                        scrapFactor, fi.is_deleted as deleted, fi.pct_composition as percentage,fi.ITEM_TYPE as type, 
                        fi.class_type as classType, fi.SEQUENCE_NUMBER as sequenceNumber, fu.name as baseUOM, 
                        fu.name as selectedUOM, fu.name as uom_name, fu.category, fau.factor, fi.item_id as itemId,
                        fi.org_id as orgId, fi.revision_id as revisionId, fi.revision_code as revisionCode, 
                        DATE_FORMAT(fi.created_date, '%b %e, %Y %r') as createdDate, fi.created_by as createdBy, 
                        DATE_FORMAT(fi.last_modified_date, '%b %e, %Y %r') as lastModifiedDate, 
                        fi.last_modified_by as lastModifiedBy, fi.substitute_parent as substituteParent from 
                        {TableName.frm_formula} fm join  {TableName.frm_formula_item} fi 
                        on fm.id = fi.FK_PRODUCED_BY_FORMULA join 
                        {TableName.frm_fitem_alt_uom} fau on fi.id = fau.FK_FORMULA_ITEM join {TableName.frm_uom} fu on 
                        fau.fk_alternate_uom = fu.id  where fm.id = '{formula_tree_id}' """

            # query_params = (formula_tree_id,)
            flag, data = db_utility.select_mysql_table(query)

            if flag and data:

                formula_tree = self.uom_generator(data)

                main_dict.update(formula_tree)

                attribute_query = f"""select ad.Name as name,av.value_string as value 
                                      from {TableName.frm_fitem_attr_val} av 
                                      join {TableName.frm_attribute_def} ad on av.FK_ATTRIBUTE_DEF = ad.id 
                                      where av.FK_FORMULA_ITEM='{formula_tree.get("dbId", None)}'"""
                attribute_flag, attribute_data = db_utility.select_mysql_table(attribute_query)

                if attribute_flag:
                    main_dict.update({"attributes": self.attribute_generator(attribute_data)})

                main_dict['formula'] = self.formula_generator(formula_tree_id)
                main_dict['formula']['requirements'] = dict()
                main_dict['enableGrndChldOps'] = ChildrenConfigs.enableGrndChldOps
                body_content_data.append(main_dict)

                # to add key to the hierarchy tree children
                # body_content_data = self.add_key_to_children(body_content_data)

                response.update(
                    {"status": "success", "message": "data fetched Successfully", "data": body_content_data})

            else:
                response.update(
                    {"status": "success", "message": "No data is available for the given id",
                     "data": body_content_data})

            logger.info("Completed fetching formula tree JSON data")
            return response
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def add_key_to_children(self, data, parent_key=""):
        try:
            # print(data)
            for i, item in enumerate(data):
                key = f"{parent_key}-{i + 1}" if parent_key else str(i + 1)

                item["key"] = key
                children_formula = item.get("formula", {}).get("children", [])
                if children_formula:
                    self.add_key_to_children(children_formula, key)
            return data
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

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
            logger.exception(e)
            raise HTTPException(status_code=401, detail=f"Failed in UID generation: {str(e)}")

    def query_executor(self, query, params=None):
        """
            Executes the query and returns data
        """
        try:

            flag, data = db_utility.select_mysql_table(query, params)

            if flag:
                return data

            else:
                return dict()

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def attribute_insertion(self, attribute_data, queries_dict, db_id):
        try:
            """key_to_remove = ['itemsequencenumber'] uncomment this add the  logic in the below for loop
             if key.lower() not in key_to_remove to remove itemSequenceNumber"""
            attribute_query_list = [
                {"name": key, "value": value,
                 "attribute_def_id": self.unique_id_generator(TableIdPrefix.frm_attribute_def),
                 "attr_val_id": self.unique_id_generator(TableIdPrefix.frm_fitem_attr_val)} for
                key, value in
                attribute_data.items()]

            for rec in attribute_query_list:
                frm_attribute_def_insert = queries_dict.get('frm_attribute_def_insert', [])
                frm_fitem_attr_val_insert = queries_dict.get('frm_fitem_attr_val_insert', [])

                frm_attribute_def_insert.extend(
                    [(rec.get("attribute_def_id"), rec.get("name"), 'String', 0, 0, 1, 1)])
                frm_fitem_attr_val_insert.extend([(rec.get("attr_val_id"), rec.get("value"), str(db_id),
                                                   rec.get("attribute_def_id"))])

                queries_dict['frm_attribute_def_insert'] = frm_attribute_def_insert
                queries_dict['frm_fitem_attr_val_insert'] = frm_fitem_attr_val_insert

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def attributes_comparision(self, attribute_data, db_id, queries_dict):

        try:
            query = f"""select ad.Name as name,av.value_string as value, av.FK_ATTRIBUTE_DEF as att_id
                        from {TableName.frm_fitem_attr_val} av 
                        join {TableName.frm_attribute_def} ad on av.FK_ATTRIBUTE_DEF = ad.id where 
                        av.FK_FORMULA_ITEM = %s """

            query_params = (db_id,)
            existing_attribute_data = self.query_executor(query, query_params)

            if existing_attribute_data:

                new_keys_list = list(attribute_data)
                update_list = list()

                for rec in existing_attribute_data:

                    att_name = rec.get("name", "")
                    att_value = rec.get("value", "")
                    main_attribute_value = str(attribute_data.get(att_name, ""))

                    if att_name in new_keys_list and att_value == main_attribute_value:
                        attribute_data.pop(att_name, None)

                    elif att_name in new_keys_list and att_value != main_attribute_value:
                        rec["value"] = main_attribute_value
                        update_list.append(rec)
                        attribute_data.pop(att_name, None)

                if update_list:
                    frm_fitem_attr_val_update = queries_dict.get("frm_fitem_attr_val_update", [])
                    frm_fitem_attr_val_update.extend(
                        [(rec.get("value", ""), rec.get("att_id", ""), str(db_id)) for rec in update_list])
                    queries_dict['frm_fitem_attr_val_update'] = frm_fitem_attr_val_update

                if attribute_data:
                    self.attribute_insertion(attribute_data, queries_dict, db_id)

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_attributes(self, attribute_data, formula_id, queries_dict):

        try:

            query = f"""select attribute ,value, fk_formula  from {TableName.frm_formula_attributes} where 
                        fk_formula = %s """

            query_param = (formula_id,)
            existing_attribute_data = self.query_executor(query, query_param)

            if existing_attribute_data:

                new_keys_list = list(attribute_data)
                update_list = list()

                for rec in existing_attribute_data:
                    att_name = rec.get("attribute", "")
                    att_value = rec.get("value", "")
                    main_attribute_value = str(attribute_data.get(att_name, ""))

                    if att_name in new_keys_list and att_value == main_attribute_value:
                        attribute_data.pop(att_name, None)

                    elif att_name in new_keys_list and att_value != main_attribute_value:
                        rec["value"] = main_attribute_value
                        update_list.append(rec)
                        attribute_data.pop(att_name, None)

                if update_list:
                    frm_formula_attributes_update = queries_dict.get('frm_formula_attributes_update', [])
                    frm_formula_attributes_update.extend(
                        [(rec.get("value", ""), rec.get("attribute", ""), rec.get("fk_formula", "")) for rec
                         in update_list])

                    queries_dict['frm_formula_attributes_update'] = frm_formula_attributes_update

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def uom_adding(self, uom_json, frm_formula_item_uuid, queries_dict, frm_fitem_alt_uom_uuid):
        try:

            fau_list = queries_dict.get("frm_fitem_alt_uom_insertion", [])
            fu_list = queries_dict.get("frm_uom_insertion", [])

            for key, value in uom_json.items():

                """Below condition added to make sure fk_uom & fk_selected_uom column in formula_item table matches 
                with id column in frm_fitem_alt_uom table it matches with only one id value in frm_fitem_alt_uom table
                if two uoms are present"""
                if frm_fitem_alt_uom_uuid:
                    fau_uuid = frm_fitem_alt_uom_uuid
                    frm_fitem_alt_uom_uuid = None
                else:
                    fau_uuid = self.unique_id_generator(TableIdPrefix.frm_fitem_alt_uom)
                fu_uuid = self.unique_id_generator(TableIdPrefix.frm_uom)

                fau_dict = {"id": fau_uuid, "fk_formula_item": frm_formula_item_uuid, "fk_alternate_uom": fu_uuid,
                            "factor": value.get("factor", None)}
                fu_dict = {"id": fu_uuid, "name": value.get("name", None), "abbreviation": value.get("name", None),
                           "base_uom": value.get("base_uom", None), "conversion": value.get("conversion", None),
                           "category": value.get("category", None)}

                fau_list.extend([fau_dict])
                queries_dict['frm_fitem_alt_uom_insertion'] = fau_list

                fu_list.extend([fu_dict])
                queries_dict['frm_uom_insertion'] = fu_list

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_chld_insertion(self, user_id, formula_id, chld_json, queries_dict, seq_num, frm_name=None):
        try:
            """# frm_formula_uuid = self.unique_id_generator(TableIdPrefix.frm_formula)"""

            frm_formula_item_uuid = self.unique_id_generator(TableIdPrefix.frm_formula_item)
            frm_fitem_alt_uom_uuid = self.unique_id_generator(TableIdPrefix.frm_fitem_alt_uom)
            fk_produced_formula_uuid = None
            item_type = None
            frm_json = chld_json.get("formula", {})
            uom_json = chld_json.get("availableUOMs", {})
            attributes_json = chld_json.get("attributes", {})

            plm_id_json = {
                "revision_code": chld_json.get("revisionCode", None),
                "revision_id": chld_json.get("revisionId", None),
                "item_id": chld_json.get("itemId", None),
                "org_id": chld_json.get("orgId", None)
            }

            if frm_json:
                frm_json.update(plm_id_json)
                fk_produced_formula_uuid = formula_id if frm_name else \
                    self.unique_id_generator(TableIdPrefix.frm_formula)
                item_type = 'output'
                self.formula_insertion_to_db(frm_formula_item_uuid, fk_produced_formula_uuid,
                                                       frm_json, queries_dict, user_id=user_id,
                                                       frm_name=frm_name if frm_name else None)

            formula_item_data = {
                "id": frm_formula_item_uuid,
                "name": chld_json.get("name", None),
                "fk_formula": None if frm_name else formula_id,
                "quantity": chld_json.get("quantity", None),
                "fk_uom": frm_fitem_alt_uom_uuid,
                "pct_scrap_factor": chld_json.get("scrapFactor", None),
                "is_deleted": chld_json.get("deleted", 0),
                "material_ref": None,
                "item_type": item_type,
                "pct_composition": chld_json.get("percentage", None),
                "ref_id": chld_json.get("refId", None),
                "fk_produced_by_formula": fk_produced_formula_uuid,
                # "sequence_number": chld_json.get("sequenceNumber", None) if after_sync else seq_num,
                "sequence_number": seq_num,
                "food_contact": chld_json.get("foodContact", None),
                "class_type": chld_json.get("classType", None),
                "fk_selected_uom": frm_fitem_alt_uom_uuid,
                "last_modified_date": self.time_stamp_generation(),
                "created_date": self.time_stamp_generation(),
                "created_by": user_id,
                "last_modified_by": user_id,
                "substitute_parent": chld_json.get("substituteParent", None)
            }
            # self.substitution_insert_update(user_id, formula_id, chld_json, queries_dict, True)
            formula_item_data.update(plm_id_json)
            frm_formula_item_insert_dict = queries_dict.get("frm_formula_item_insert", [])
            frm_formula_item_insert_dict.extend([formula_item_data])
            queries_dict["frm_formula_item_insert"] = frm_formula_item_insert_dict

            self.uom_adding(uom_json, frm_formula_item_uuid, queries_dict, frm_fitem_alt_uom_uuid)
            self.attribute_insertion(attributes_json, queries_dict, frm_formula_item_uuid)

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def get_user_id(self, user):
        try:
            user_id_query = f""" Select user_id from {TableName.frm_users} where username = %s """
            flag, user_id_data = db_utility.select_mysql_fetchone(user_id_query, (user,))

            user_id = user_id_data.get("user_id", "") if user_id_data else ''
            return user_id
        except Exception as e:
            logger.error("Error in get_user_id: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_insertion_to_db(self, db_id, frm_formula_uuid, formula_json, queries_dict, user_id, frm_name=None):
        try:
            """need to change the created_by need to get it from the headers
            # user_id = self.get_user_id(user)"""
            frm_formula_json = {
                "id": frm_formula_uuid,
                "name": frm_name if frm_name else formula_json.get("name", ""),
                "created_date": self.time_stamp_generation(),
                "created_by": user_id,
                "fk_formula_item_output": str(db_id),
                "ref_id": formula_json.get("refId", None),
                "last_modified_date": self.time_stamp_generation(),
                "server_id": formula_json.get("serverId", None),
                "is_editable": formula_json.get("childrenEditable", True),
                "item_id": formula_json.get("item_id", None),
                "org_id": formula_json.get("org_id", None),
                "revision_id": formula_json.get("revision_id", None),
                "revision_code": formula_json.get("revision_code", None),
                "bom_id": formula_json.get("bomId", None),
                "bom_type": formula_json.get("bomType", None),
                "last_modified_by": user_id
            }

            formula_list = queries_dict.get("frm_formula_insertion", [])
            formula_list.extend([frm_formula_json])
            queries_dict['frm_formula_insertion'] = formula_list

            formula_attribute_data = [{"fk_formula": frm_formula_uuid, "attribute": key, "value": value}
                                      for key, value in formula_json.get("attributes", {}).items()]

            att_lst = queries_dict.get('frm_formula_attributes_insertion', [])
            att_lst.extend(formula_attribute_data)
            queries_dict['frm_formula_attributes_insertion'] = att_lst

            chld_lst = formula_json.get("children", [])
            chld_lst = self.substitution_insert_update(chld_lst)
            for idx, chld in enumerate(chld_lst):
                self.formula_chld_insertion(user_id, frm_formula_uuid, chld, queries_dict, seq_num=idx)

        except Exception as e:
            logger.exception("Error in formula_insertion_to_db: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def substitution_insert_update(self, chld_lst):
        try:
            chld_list = []
            for chld in chld_lst:
                if chld.get("substitutes", []):
                    chld_list.extend(chld["substitutes"])
                    chld.pop("substitutes")
                chld_list.append(chld)
            return chld_list
            # for idx,rec in enumerate(chld_json.get("substitutes", [])):
            #     if rec.get("dbId", None):
            #         self.insertion_updation_query_generator(user_id, rec, queries_dict)
            #     else:
            #         self.formula_chld_insertion(user_id, formula_id, rec, queries_dict, seq_num=idx, exec_sub=False)

        except Exception as e:
            logger.exception("Error in substitution_insert_update %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def save_formula(self, user_id, input_json, queries_dict):

        try:
            formula_json = input_json.get("formula", dict())
            formula_json_id = input_json.get("dbId", "")
            formula_id = str(formula_json.get("dbId", ""))

            frm_formula_uuid = self.unique_id_generator(TableIdPrefix.frm_formula)

            if formula_id:

                self.formula_attributes(formula_json.get("attributes", {}), formula_id, queries_dict)
                chld_lst = formula_json.get("children", [])
                chld_lst = self.substitution_insert_update(chld_lst)
                for idx, rec in enumerate(chld_lst):

                    if rec.get("dbId", ""):
                        self.insertion_updation_query_generator(user_id, rec, queries_dict)

                    else:
                        self.formula_chld_insertion(user_id, formula_id, rec, queries_dict, seq_num=idx)

                frm_formula_update_list = queries_dict.get("frm_formula_update", [])

                frm_formula_update_list.extend([(self.time_stamp_generation(), user_id,
                                                 formula_json.get("childrenEditable", True), formula_id)])
                queries_dict['frm_formula_update'] = frm_formula_update_list

            elif formula_json and formula_json_id:

                self.formula_insertion_to_db(formula_json_id, frm_formula_uuid, formula_json, queries_dict,
                                                       frm_name=None, user_id=user_id)

                frm_formula_item_list = queries_dict.get("frm_formula_item_update", [])
                frm_formula_item_list.extend([(input_json.get("quantity", None),
                                               input_json.get("scrapFactor", None),
                                               input_json.get("deleted", None),
                                               input_json.get("percentage", None),
                                               self.time_stamp_generation(),
                                               user_id, frm_formula_uuid,
                                               str(formula_json_id))])
                queries_dict['frm_formula_item_update'] = frm_formula_item_list

                """frm_json = {"key": formula_json_id, "value": input_json, "type": "formula"}
                print("printing formula: \n", frm_json)"""

        except Exception as e:
            logger.exception("Error in save_formula: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_item_updates_insertion(self, input_json):

        try:

            db_id = input_json.get("dbId", None)

            data_status = ""
            frm_formula_item_key = None
            query = f"""select fi.id as dbId, fi.ref_id as refId, fi.name, fi.quantity, fi.pct_scrap_factor as 
                        scrapFactor,fi.is_deleted as deleted, fi.pct_composition as percentage, fi.ITEM_TYPE as type, 
                        fi.class_type as classType, fi.SEQUENCE_NUMBER as sequenceNumber, fi.FK_PRODUCED_BY_FORMULA as 
                        fk_produced_by_formula from {TableName.frm_formula_item} fi where fi.id = %s """

            query_params = (db_id,)
            query_data = self.query_executor(query, query_params)
            if query_data:
                existing_data = query_data[0]

                if existing_data:

                    new_keys_list = list(input_json)
                    update_dict = {}

                    for key, value in existing_data.items():
                        if key in new_keys_list and str(value) != str(input_json.get(key, "")):
                            update_dict[key] = value
                            continue

                    if update_dict:
                        data_status = "modified"

                    frm_formula_item_key = existing_data.get("fk_produced_by_formula", "")
            return data_status, frm_formula_item_key

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    # if update_dict:
    def insertion_updation_query_generator(self, user_id, input_json, queries_dict):
        try:
            db_id = input_json.get("dbId", None)

            """# formula_dict = input_json.pop("formula") if input_json.get("formula", None) else dict()"""

            if db_id:
                self.attributes_comparision(input_json.get("attributes", {}),
                                            db_id, queries_dict)

                frm_formula_item_list = queries_dict.get("frm_formula_item_update", [])
                frm_formula_item_list.extend([(input_json.get("quantity", None),
                                               input_json.get("scrapFactor", None),
                                               input_json.get("deleted", None),
                                               input_json.get("percentage", None),
                                               self.time_stamp_generation(),
                                               user_id, input_json.get("formula", {}).get("dbId", None),
                                               str(db_id))])
                queries_dict['frm_formula_item_update'] = frm_formula_item_list

            if input_json.get("formula", None):
                self.save_formula(user_id, input_json, queries_dict)

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def queries_statement_dict(self):
        try:
            query_statement_dict = QueryStatements.query_statement_dict
            return query_statement_dict
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_name_validation(self, user_id, input_json, query_statement_dict, queries_dict):
        try:
            frm_json = input_json.get("formula", {})
            if frm_json:
                frm_name = frm_json.get("name", '')
                frm_id = frm_json.get("dbId", None)
                query = f"""select ff.id as dbId, ff.name from frm_formula ff join FRM_FORMULA_ATTRIBUTES ffa 
                            ON ff.ID = FFA.FK_FORMULA and FFA.ATTRIBUTE = 'CurrentStatus'
                            AND lower(FFA.VALUE) <> 'archived' where lower(name) = '{frm_name}' and id <> '{frm_id}'"""
                flag = self.name_validation(frm_name, exec_qry=query)
                if flag:
                    query_statement_dict['formula_name_update'] = f"""update {TableName.frm_formula} set name=%s,
                                                                     LAST_MODIFIED_DATE=%s, last_modified_by=%s
                                                                    where id=%s """
                    queries_dict['formula_name_update'] = [(frm_name, self.time_stamp_generation(), user_id, frm_id)]
                return flag
        except Exception as e:
            logger.exception("Error in formula name validation %s", e)
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def save_formula_tree_handler(self, user, input_json):
        try:
            logger.info("Inside save_formula_tree_handler")
            queries_dict = dict()
            status = "failed"
            message = "Unable to Save the Formula"
            user_id = self.get_user_id(user)
            query_statement_dict = self.queries_statement_dict()

            flag = self.formula_name_validation(user_id, input_json, query_statement_dict, queries_dict)
            if flag:
                self.insertion_updation_query_generator(user_id, input_json, queries_dict)

                if queries_dict:
                    flag = db_utility.execute_query_transactions(query_statement_dict, queries_dict)

                    if flag:
                        status = "success"
                        message = "Data Updated Successfully"
                return {"status": status, "message": message}
            else:
                return {"status": status, "message": "Formula name already exists. Please try to save it with other name"}
        except Exception as e:
            logger.exception(str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def uom_insertion(self, queries_dict, formula_item_uuid, db_id, frm_fitem_alt_uom_uuid):
        try:
            query = f"""select * from {TableName.frm_fitem_alt_uom} fau join {TableName.frm_uom} fu on 
                            fau.FK_ALTERNATE_UOM = fu.id where fk_formula_item = %s """
            
            query_param = (db_id,)
            uom_data = self.query_executor(query, query_param)
            for rec in uom_data:

                if frm_fitem_alt_uom_uuid:
                    fau_uuid = frm_fitem_alt_uom_uuid
                    frm_fitem_alt_uom_uuid = None

                else:
                    fau_uuid = self.unique_id_generator(TableIdPrefix.frm_fitem_alt_uom)
                fu_uuid = self.unique_id_generator(TableIdPrefix.frm_uom)
                rec = {key.lower(): value for key, value in rec.items()}

                fau_dict = {"id": fau_uuid, "fk_formula_item": formula_item_uuid, "fk_alternate_uom": fu_uuid,
                            "factor": rec.get("factor", None)}

                fu_dict = {"id": fu_uuid, "name": rec.get("name", None), "abbreviation": rec.get("abbreviation", None),
                           "base_uom": rec.get("base_uom", None), "conversion": rec.get("conversion", None),
                           "category": rec.get("category", None)}
                fau_list = queries_dict.get("frm_fitem_alt_uom_insertion", [])
                fau_list.extend([fau_dict])
                queries_dict['frm_fitem_alt_uom_insertion'] = fau_list
                fu_list = queries_dict.get("frm_uom_insertion", [])
                fu_list.extend([fu_dict])
                queries_dict['frm_uom_insertion'] = fu_list
        except Exception as e:
            logger.exception("Error in uom_insertion ", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def children_insertion(self, formula_id, children_id, chld_formula_id, queries_dict):
        try:
            """ To be commented frm_formula_uuid = self.unique_id_generator(TableIdPrefix.frm_formula)"""

            frm_formula_item_uuid = self.unique_id_generator(TableIdPrefix.frm_formula_item)
            frm_fitem_alt_uom_uuid = self.unique_id_generator(TableIdPrefix.frm_fitem_alt_uom)

            query = f"""select * from frm_formula_item where id = '{children_id}'"""

            chld_data = self.query_executor(query)
            if chld_data:
                chld_data = {key.lower(): value for key, value in chld_data[0].items()}
                formula_item_id = chld_data.get("id")
                chld_data.update({"id": frm_formula_item_uuid, "fk_uom": frm_fitem_alt_uom_uuid,
                                  "fk_selected_uom": frm_fitem_alt_uom_uuid, "fk_formula": formula_id})

                if chld_formula_id:
                    frm_formula_uuid = self.unique_id_generator(TableIdPrefix.frm_formula)
                    chld_db_id = chld_data.get("fk_produced_by_formula", "")
                    chld_data.update({"fk_produced_by_formula": frm_formula_uuid})
                    self.formula_insertion(frm_formula_uuid, frm_formula_item_uuid, chld_db_id, queries_dict)

                frm_formula_item_insert_dict = queries_dict.get("frm_formula_item_insert", [])
                frm_formula_item_insert_dict.extend([chld_data])
                queries_dict["frm_formula_item_insert"] = frm_formula_item_insert_dict

                attributes_query = f"""select ad.Name as name,av.value_string as value, av.FK_ATTRIBUTE_DEF as att_id
                                            from {TableName.frm_fitem_attr_val} av 
                                            join {TableName.frm_attribute_def} ad on av.FK_ATTRIBUTE_DEF = ad.id where 
                                            av.FK_FORMULA_ITEM = %s """

                attributes_query_param = (formula_item_id,)
                attribute_data = self.query_executor(attributes_query, attributes_query_param)
                attribute_data = self.attribute_generator(attribute_data)
                self.attribute_insertion(attribute_data, queries_dict, frm_formula_item_uuid)

                self.uom_insertion(queries_dict, frm_formula_item_uuid, formula_item_id,
                                             frm_fitem_alt_uom_uuid)
        except Exception as e:
            logger.exception("Error in children_insertion: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def time_stamp_generation(self):
        try:
            current_date = datetime.now()
            iso_formatted_str = current_date.isoformat(timespec='milliseconds')

            """current_date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]"""
            return datetime.fromisoformat(iso_formatted_str)

        except Exception as e:
            logger.exception("Error in children_insertion: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_insertion(self, frm_formula_uuid, frm_formula_item_uuid, db_id, queries_dict, name=None):
        try:
            formula_query = f"""select * from {TableName.frm_formula} where id = %s """
            formula_query_param = (db_id,)

            formula_data = self.query_executor(formula_query, formula_query_param)
            if formula_data:
                formula_data = {key.lower(): value for key, value in formula_data[0].items()}

                if name:
                    formula_data.update({"name": name})

                formula_data.update({"id": frm_formula_uuid, "fk_formula_item_output": frm_formula_item_uuid,
                                     "created_date": self.time_stamp_generation(),
                                     "last_modified_date": self.time_stamp_generation()})

                formula_list = queries_dict.get("frm_formula_insertion", [])
                formula_list.extend([formula_data])
                queries_dict['frm_formula_insertion'] = formula_list

                formula_attribute_query = f"""select '{frm_formula_uuid}' as fk_formula, attribute, value from 
                                                {TableName.frm_formula_attributes} where fk_formula = %s """
                formula_attribute_query_param = (db_id,)

                formula_attribute_data = self.query_executor(formula_attribute_query, formula_attribute_query_param)
                att_lst = queries_dict.get('frm_formula_attributes_insertion', [])
                att_lst.extend(formula_attribute_data)
                queries_dict['frm_formula_attributes_insertion'] = att_lst

                list_of_children_query = f"""select id, fk_produced_by_formula from {TableName.frm_formula_item} 
                                                                    where fk_formula = %s """

                list_of_children_query_param = (db_id,)
                children_data = self.query_executor(list_of_children_query, list_of_children_query_param)
                if children_data:
                    for chld in children_data:
                        chld_id = chld.get("id", None)
                        chld_formula_id = chld.get('fk_produced_by_formula', None)
                        if chld_id:
                            self.children_insertion(frm_formula_uuid, chld_id, chld_formula_id, queries_dict)
        except Exception as e:
            logger.exception("Error in formula_insertion: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_item_details(self, queries_dict, db_id, name):
        try:
            message = "Formula Cloned Successfully"
            frm_formula_uuid = self.unique_id_generator(TableIdPrefix.frm_formula)
            frm_formula_item_uuid = self.unique_id_generator(TableIdPrefix.frm_formula_item)
            frm_fitem_alt_uom_uuid = self.unique_id_generator(TableIdPrefix.frm_fitem_alt_uom)

            formula_item_query = f"""select * from {TableName.frm_formula_item} 
                                    where FK_PRODUCED_BY_FORMULA = %s """
            formula_item_query_param = (db_id,)

            formula_item_data = self.query_executor(formula_item_query, formula_item_query_param)
            if formula_item_data:
                data = formula_item_data[0]
                data = {key.lower(): value for key, value in data.items()}

                formula_item_id = data.get("id", "")
                data.update({"id": frm_formula_item_uuid, "fk_uom": frm_fitem_alt_uom_uuid,
                             "fk_selected_uom": frm_fitem_alt_uom_uuid, "fk_produced_by_formula": frm_formula_uuid})

                frm_formula_item_insert_dict = queries_dict.get("frm_formula_item_insert", [])
                frm_formula_item_insert_dict.extend([data])
                queries_dict["frm_formula_item_insert"] = frm_formula_item_insert_dict

                attributes_query = f"""select ad.Name as name,av.value_string as value, av.FK_ATTRIBUTE_DEF as att_id
                                from {TableName.frm_fitem_attr_val} av 
                                join {TableName.frm_attribute_def} ad on av.FK_ATTRIBUTE_DEF = ad.id where 
                                av.FK_FORMULA_ITEM = %s """
                attributes_query_param = (formula_item_id,)

                attribute_data = self.query_executor(attributes_query, attributes_query_param)
                if attribute_data:
                    attribute_data = self.attribute_generator(attribute_data)
                    self.attribute_insertion(attribute_data, queries_dict, frm_formula_item_uuid)

                self.uom_insertion(queries_dict, frm_formula_item_uuid, formula_item_id, frm_fitem_alt_uom_uuid)
                self.formula_insertion(frm_formula_uuid, frm_formula_item_uuid, db_id, queries_dict, name)

            else:
                message = "Formula trying to copy Does not Exists"
            return frm_formula_uuid, message
        except Exception as e:
            logger.error("Error in formula_item_details: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def name_validation(self, name, exec_qry=None):
        try:
            query = f"""select ff.id as dbId, ff.name from frm_formula ff join FRM_FORMULA_ATTRIBUTES ffa 
                        ON ff.ID = FFA.FK_FORMULA and FFA.ATTRIBUTE = 'CurrentStatus'
                            AND lower(FFA.VALUE) <> 'archived' where lower(name) = '{name}'"""
            if exec_qry:
                query = exec_qry
            flag = False
            data_flag, table_data = db_utility.select_mysql_table(query)
            if data_flag and not table_data:
                flag = True
            return flag
        except Exception as e:
            logger.error("Error while validating the data %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def save_formula_tree_as(self, user, name, frm_json, name_checked=False):
        try:
            logger.info("Inside save_formula_tree_as")
            response = ResponseMessage.final_json("failed", "unable to Copy the Formula Data", [])
            queries_dict = {}
            data = {}
            flag = name_checked if name_checked else self.name_validation(name)
            user_id = self.get_user_id(user)
            if flag and user_id:
                flag = False
                query_statements_dict = self.queries_statement_dict()

                formula_id = self.unique_id_generator(TableIdPrefix.frm_formula)
                self.formula_chld_insertion(user_id, formula_id, frm_json, queries_dict,
                                                      seq_num=frm_json.get("sequenceNumber", 0),
                                                      frm_name=name)

                if queries_dict:
                    flag = db_utility.execute_query_transactions(query_statements_dict, queries_dict)
                    data.update({"name": name, "formula_id": formula_id})
                    response = ResponseMessage.final_json("success", "Formula Saved Successfully",
                                                          data) if flag else response
                else:
                    response = ResponseMessage.final_json("failed", "Unable to copy the formula",
                                                          data) if flag else response
            else:
                response = ResponseMessage.final_json("failed", "The formula name already exists. Please try creating "
                                                                "it with a different name" if not flag else
                                                                "Unable to Save the Formula for the current user", [])
            logger.info("Completed save_formula_tree_as")
            return response
        except Exception as e:
            logger.error("Error in save_formula_tree_as: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def formula_children_delete_insertion(self, user, frm_json):
        try:
            db_id = frm_json.get("db_id", None)
            fri_db_id = frm_json.get("fri_db_id")

            resp = ResponseMessage.final_json("failed", "Unable to refresh the data")
            if db_id:
                home_handler = HomeHandler()
                logger.info("Started Children Deletion Operation")
                queries_dict = home_handler.children_deletion_after_sync(db_id)

                """ 
                # chld_json = frm_json.get("data", {}).get("formula",{}).get("children", [])
                # if not queries_dict:
                #     return resp """

                save_input_json = frm_json.get("data", {})
                save_input_json["dbId"] = fri_db_id
                save_input_json["formula"]["dbId"] = db_id
                user_id = self.get_user_id(user)
                self.insertion_updation_query_generator(user_id, save_input_json, queries_dict)

                # Initializing data to be updated during PLM refresh
                rev_code = save_input_json.get("revisionCode", "")
                rev_id = save_input_json.get("revisionId", "")

                if queries_dict:
                    logger.info("Started Execution of Queries")
                    query_statements = self.queries_statement_dict()
                    query_statements['frm_date_updt'] = f""" update {self.tables.frm_formula} set last_modified_date = %(last_modified_date)s, 
                    revision_code = %(revision_code)s, revision_id = %(revision_id)s where id = %(id)s """
                    queries_dict['frm_date_updt'] = [{"last_modified_date":self.time_stamp_generation(), "revision_code": rev_code,
                                                      "revision_id": rev_id, "id": db_id}]

                    query_statements['frm_item_tab_updt'] = f""" update {self.tables.frm_formula_item} set last_modified_date
                                                            = %(last_modified_date)s, revision_code = %(revision_code)s,
                                                            revision_id = %(revision_id)s 
                                                            where id = %(id)s """
                    queries_dict['frm_item_tab_updt'] = [{"last_modified_date":self.time_stamp_generation(), "revision_code": rev_code,
                                                          "revision_id": rev_id, "id": fri_db_id}]


                    flag = db_utility.execute_query_transactions(query_statements, queries_dict)
                    if flag:
                        logger.info("Data Refreshed Successfully")
                        resp = ResponseMessage.final_json("success", "Data Successfully Refreshed")
            return resp
        except Exception as e:
            logger.error("Error in formula_children_delete_insertion: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def fetch_notes_handler(self, db_id):
        try:
            logger.info("Inside fetch_notes_handler")
            response = ResponseMessage.final_json("failed", "Unable to Fetch the Notes", [])
            logger.info("Fetching Notes")
            query = f"""select id as dbId, DATE_FORMAT(lastmodifieddate, '%b %e, %Y %r') as entryDate, entry,
                        username from {self.tables.frm_notes} where formula_id = '{db_id}' order by lastmodifieddate desc """

            # query_param = (db_id,)
            flag, data = db_utility.select_mysql_table(query)

            if flag:
                response = ResponseMessage.final_json("success", "Data Fetched Successfully", data)

            logger.info("Completed fetch_notes_handler")
            return response

        except Exception as e:
            logger.error("Error in fetch_notes_handler: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def insertion_notes_handler(self, formula_id, entry, user_name):
        try:
            logger.info("Inside insertion_notes_handler")
            resp = ResponseMessage.final_json("failed", "Unable to insert the notes try again", [])
            if user_name:
                data = (self.unique_id_generator(TableIdPrefix.frm_notes),
                        self.time_stamp_generation(),
                        entry.strip(), formula_id, user_name)

                query = f"""insert into {TableName.frm_notes}(id, lastmodifieddate, entry, formula_id, username) 
                            values(%s, %s, %s, %s, %s)"""
                flag = db_utility.insert_mysql_table(query, data)
                if flag:
                    resp = ResponseMessage.final_json("success", "Notes inserted successfully", [])
            
            logger.info("Completed insertion_notes_handler")
            return resp

        except Exception as e:
            logger.error("Error in insertion_notes_handler: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def manage_shared_access(self, input_json):
        try:
            logger.info("Inside manage_shared_access")
            responses = {}

            if input_json.add:
                for item in input_json.add:
                    user_id = item.user_id
                    formula_id = item.formula_id
                    access = item.access
                    if user_id and access and formula_id:
                        select_query = f"""SELECT COUNT(*) as cnt FROM {TableName.frm_shared_users} WHERE user_id = %s AND formulaid = %s """
                        select_query_param = (user_id, formula_id,)
                        user_exists, count = self.db_conn.select_mysql_table(select_query, select_query_param)

                        if user_exists and count[0].get('cnt', 0) != 0:
                            update_query = f""" UPDATE {TableName.frm_shared_users} SET access = %s 
                            WHERE user_id = %s AND formulaid = %s """
                            update_query_params = (access, user_id, formula_id)
                            flag = self.db_conn.update_mysql_table(update_query, update_query_params)
                            if flag:
                                responses.update({'status': 'success',
                                                  'message': 'User access updated successfully ! '})
                        else:
                            # If the combination does not exist, insert a new record
                            insert_query = f""" INSERT INTO {TableName.frm_shared_users} (user_id, formulaid, access)
                                VALUES (%s, %s, %s)
                            """
                            insert_query_params = (user_id, formula_id, access)
                            flag = self.db_conn.insert_mysql_table(insert_query, insert_query_params)

                            if flag:
                                responses.update({'status': 'success',
                                                  'message': 'User access updated successfully !'})
                    else:
                        responses.update({'status': 'failed',
                                          'message': 'User access update failed'})

            if input_json.edit:
                for item in input_json.edit:
                    user_id = item.user_id
                    formula_id = item.formula_id
                    access = item.access
                    if user_id and access and formula_id:
                        update_query = f"""
                            UPDATE frm_shared_users
                            SET access = '{access}'
                            WHERE user_id = '{user_id}' AND formulaid = '{formula_id}'
                            """
                        flag = self.db_conn.update_mysql_table(update_query)

                        if flag:
                            responses.update({'status': 'success',
                                              'message': 'User access updated successfully !'})
                    else:
                        responses.update({'status': 'failed',
                                          'message': 'User access update failed'})

            if input_json.delete:
                for item in input_json.delete:
                    user_id = item.user_id
                    formula_id = item.formula_id
                    if user_id and formula_id:
                        delete_query = f"""
                                            DELETE FROM frm_shared_users
                                            WHERE user_id = '{user_id}' AND formulaid = '{formula_id}'
                                        """
                        flag = self.db_conn.delete_mysql_table(delete_query)

                        if flag:
                            responses.update({'status': 'success',
                                              'message': 'User access updated successfully !'})
                    else:
                        responses.update({'status': 'failed',
                                          'message': 'User access update failed'})

                if not responses:
                    responses.update({"status": "failed", "message": "No valid operation found in the input JSON"})

            logger.info("Completed manage_shared_access")
            return responses
        except Exception as e:
            logger.error("Error processing shared access data: %s", str(e))
            return [{"status": "failed", "message": "Error processing shared access data"}]

    def fetch_access_info(self, formula_id):
        try:
            logger.info("Inside fetch_access_info")
            query = f"""SELECT {TableName.frm_shared_users}.user_id, {TableName.frm_shared_users}.access, {TableName.frm_users}.name FROM {TableName.frm_shared_users} JOIN {TableName.frm_users} ON {TableName.frm_shared_users}.user_id = {TableName.frm_users}.user_id WHERE {TableName.frm_shared_users}.formulaid = %s """
            query_param = (formula_id,)
            flag, user_data = self.db_conn.select_mysql_table(query, query_param)

            if user_data:
                output_data = []

                for user in user_data:
                    user_info = {
                        "user_id": user["user_id"],
                        "name": user["name"],
                        "formula_id": formula_id,
                        "access": user["access"]
                    }
                    output_data.append(user_info)

                return {
                    "status": "success",
                    "message": "Details fetched successfully",
                    "data": output_data
                }
            else:
                return {
                    "status": "success",
                    "message": "No shared users",
                    "data": []
                }
        except Exception as e:
            logger.error(f"Error while assigning access level: {str(e)}")
            return {'status': 'error', 'message': 'Unable to fetch data'}

    def fetch_username_data(self, username, formulaid):
        try:
            logger.info("Inside fetch_username_data")
            user_query = f"""
            SELECT u.user_id,u.name,u.username from {TableName.frm_users} u where u.activestatus = 'y' AND u.username <> %s
            AND u.user_id NOT IN (Select su.user_id from {TableName.frm_shared_users} su where su.formulaid = %s ) """
            user_query_params = (username, formulaid)
            flag, user_data = self.db_conn.select_mysql_table(user_query, user_query_params)

            logger.info("Completed fetch_username_data")
            if user_data:
                return {'status': 'success', 'message': 'Details fetched successfully', 'data': user_data}
            else:
                return {'status': 'failed', 'message': 'Unable to fetch details', "data": []}
        except Exception as e:
            logger.error(f"Error while fetching the Users details: {str(e)}")
            return {'status': 'error', 'message': 'Unable to fetch the Users details'}

    def summary_sheet(self, workbook, frm_data):
        try:
            frm_name = frm_data.get('name', '') + ' ' + frm_data.get("refId", '')
            ws = workbook.add_worksheet("summary")

            heading_format = {
                "bold": True,
                "font_size": 12,
                "font_name": 'Arial'
            }
            fmt = workbook.add_format(heading_format)
            ws.write('A1', "Formula Name", fmt)
            ws.set_column(0, 0, 35)
            ws.write('C1', frm_name)
            ws.write('A3', "Timestamp", fmt)
            ws.set_column(2, 0, 35)
            current_datetime = datetime.utcnow()
            ws.write('C3', current_datetime.strftime("%a %b %d %H:%M:%S UTC %Y"))
        except Exception as e:
            logger.error("Error while creating summary Sheet %s", str(e))

    def new_hdrs_add(self, resp):
        try:
            resp = resp.get('data', []) if resp.get("status", '').lower() == 'success' else list()
            keys_lst = list()
            hdr_dct = {}
            for rec in resp:
                chld_data = rec.get("children", [])
                header_name = chld_data[0].get("headerName", '') if chld_data else str()
                fld_lst = [chld.get('field', '') for chld in chld_data]
                keys_lst.extend(fld_lst)
                hdr_dct[header_name] = ','.join(fld_lst)
            return keys_lst, hdr_dct
        except Exception as e:
            logger.error("Error while adding the new Headers %s", str(e))

    def headers_creation(self, workbook, sheet, username, formulaid):
        try:
            # resp to be changed to attribute definitions api

            resp = table_config_obj.get_attribute_definition(username, formulaid)
            # resp = self.get_attribute_definition_handler("test1")
            keys_lst, hdr_dct = self.new_hdrs_add(resp)

            xl_headers = {
                "general": "Reference ID,Level,Item Name,Qty,UOM",
                "scrap": "Scrap Factor,Required Qty,Input Yield,Output Yield",
            }
            xl_headers.update(hdr_dct)

            header_style = workbook.add_format({
                'bold': True,
                'font_size': 10,
                'font_name': 'Arial',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            })
            col_count = 0
            for key, value in xl_headers.items():
                row = 1
                cols = value.split(",")
                cols_len = len(cols)
                column = col_count
                if cols_len == 1:
                    sheet.write(0, column, key.title(), header_style)
                    sheet.set_column(0, column, 30)
                else:
                    sheet.merge_range(0, col_count, 0, col_count + cols_len - 1, key.title(), header_style)
                for item in cols:
                    sheet.write(row, column, item, header_style)
                    sheet.set_column(row, column, 30)
                    column = column + 1
                col_count = col_count + cols_len
            return keys_lst

        except Exception as e:
            logger.error("Error while creating the headers %s", str(e))

    def json_generator(self, frm_data, att_lst, data_lst):
        try:
            formula_json = frm_data.get("formula", {})
            dt = {
                "ref_id": frm_data.get("refId", None),
                "level": frm_data.get("key", None),
                "item_name": frm_data.get("name", None),
                "qty": frm_data.get("quantity", None),
                "uom": frm_data.get("baseUOM", None),
                "scrap_factor": frm_data.get("scrapFactor", None),
                "required_qty": None,
                "input_yield": None,
                "output_yield": None,
                "percentage": frm_data.get("percentage", None),
                "percentage_level_2": None,
                "percentage_level_3": None,
                "percentage_level_4": None
            }

            for rec in att_lst:
                if rec.lower().startswith("percentage"):
                    continue
                dt[rec] = frm_data.get("attributes", {}).get(rec, None)
            data_lst.append(dt)
            if formula_json:
                for rec in frm_data.get("formula", {}).get("children", []):
                    self.json_generator(rec, att_lst, data_lst)
            return data_lst
        except Exception as e:
            logger.error("Error while generating the Json %s", str(e))

    def excel_generator_handler_v0(self, formula_json, user):
        try:
            output = io.BytesIO()
            formula_data = formula_json.get("formulaData", {})
            formula_id = formula_json.get("formulaId", '')
            if formula_data and formula_data:
                formula_data['key'] = '1'
                formula_data['formula']['children'] = self.add_key_to_children(
                    formula_data.get("formula", {}).get("children", []),
                    formula_data.get("key", 1))
                file_name = f"""{formula_data.get("formula", {}).get("name", str(datetime.now()))}.xlsx"""
                wb = xlw.Workbook(output)
                self.label_mockup_sheet(wb, formula_data.get("formula", {}))
                self.summary_sheet(wb, formula_data)
                frm_ws = wb.add_worksheet("formula")
                lst_to_check = self.headers_creation(wb, frm_ws, user, formula_id)
                main_list = []
                self.json_generator(formula_data, lst_to_check, main_list)
                row = 2
                for rec in main_list:
                    for col, value in enumerate(rec.values()):
                        frm_ws.write(row, col, value)
                    row = row + 1

                wb.close()
                output.seek(0)
                
                headers = {
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                }

                return StreamingResponse(output, headers=headers)

        except Exception as e:
            logger.error("Error in insertion_notes_handler: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def data_extractor(self, json_data, key_path):
        logger.debug(self.__module__)
        try:
            keys = key_path.split('.')
            result = json_data
            for key in keys:
                if '$l' not in key:
                    result = result.get(key, '')
                else:
                    index = int(key.replace('$l', ''))
                    if len(result) < index:
                        raise Exception("noData")
                    result = result[index]
            return result
        except Exception as e:
            return None

    def generate_column_data(self, input_data, temp_json, key_name, val_name, level):
        try:
            for each_children in input_data.get("formula", {}).get("children", []):
                final_val = self.data_extractor(each_children, val_name)
                if val_name == "name":
                    temp_json.append({key_name: " " * (level * 4) + str(final_val)})
                else:
                    temp_json.append({key_name: final_val})
                if each_children.get("formula", {}).get("children", []):
                    self.generate_column_data(each_children, temp_json, key_name, val_name, level + 1)
        except Exception as e:
            logger.error("Error while generating column excel data: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def write_cell_column_data(self, frm_json, cell_list, col_map_json, worksheet, excel_writer, sheet_name):
        try:
            for each_cell in cell_list:
                if each_cell.get("attribute_key"):
                    worksheet.write(each_cell.get("cell"), self.data_extractor(frm_json, each_cell["attribute_key"]))
                else:
                    worksheet.write(each_cell.get("cell"), each_cell["attribute_name"])

            for col, data in col_map_json.items():
                key = list(data.keys())[0]
                val = list(data.values())[0]
                temp_json = list()
                final_val = self.data_extractor(frm_json, val)
                temp_json.append({key: final_val})
                self.generate_column_data(frm_json, temp_json, key, val, 1)
                match = re.match(r'([A-Za-z]+)(\d+)', col)
                if match:
                    col_name = match.group(1)
                    row_num = int(match.group(2)) or 1
                    df = pd.DataFrame(temp_json)
                    df.to_excel(excel_writer, sheet_name=sheet_name, index=False, header=True, startcol=ord(col_name) - 65,
                                startrow=row_num - 1)
        except Exception as e:
            logger.error("Error while writing cell and column data in excel: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e

    def excel_generator_handler(self, input_json):
        try:
            logger.info("Inside excel_generator_handler")
            frm_json = input_json.get("tree_json", {})
            config_name = input_json.get("configName")
            select_query = f"""select * from {TableName.frm_excel_configurations} where lower(name) = '{config_name}' and config is not null; """
            flag, excel_config_data = self.db_conn.select_mysql_table(select_query)
            if not flag or not excel_config_data:
                return Response({"status": "error", "message": "Config data not found"}, status_code=404)
            input_excel_config = json.loads(excel_config_data[0].get("config", {}))

            excel_config_map = dict()
            for each_item in input_excel_config:
                excel_tab = each_item["excel_tab"]
                if excel_tab not in excel_config_map:
                    excel_config_map[excel_tab] = []
                excel_config_map[excel_tab].append(each_item)

            output = io.BytesIO()
            excel_file = f"""{frm_json.get("formula", {}).get("name", str(datetime.now()))}.xlsx"""
            excel_writer = pd.ExcelWriter(output, engine='xlsxwriter')

            workbook = excel_writer.book

            for each_sheet in excel_config_map:
                each_sheet_config = excel_config_map[each_sheet]
                sheet_name = each_sheet_config[0]["excel_tab"]

                worksheet = workbook.add_worksheet(sheet_name)
                col_map_json = dict()
                cell_list = list()
                for each_att in each_sheet_config:
                    if each_att.get("specific") in ["cell"]:
                        cell_list.append(each_att)
                    else:
                        col_map_json[each_att.get("column")] = {
                            each_att.get("attribute_name"): each_att.get("attribute_key")}

                self.write_cell_column_data(frm_json, cell_list, col_map_json, worksheet, excel_writer, sheet_name)

            excel_writer.close()
            output.seek(0)
            logger.debug(f"Excel file '{excel_file}' generated successfully.")
            headers = {
                "Content-Disposition": f"attachment; filename={excel_file}",
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }

            logger.info("Completed excel_generator_handler")
            return StreamingResponse(output, headers=headers)
        except Exception as e:
            logger.error("Error in excel generation: %s", str(e))
            raise HTTPException(status_code=401, detail=e.args, ) from e
        
