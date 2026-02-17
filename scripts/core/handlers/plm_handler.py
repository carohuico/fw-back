"""
Interacts with PLM system to fetch item details, formula tree and sync formula tree to PLM. This will interact with PLMHandler for processing the requests and fetching data from PLM system.
"""
import copy
import json
from datetime import datetime, timedelta

from scripts.core.handlers.formula_handlers import FormulaHandler
from scripts.constants import app_constants
from scripts.logging import logger
from scripts.utils.plm_utility import PLMUtility
from scripts.utils.sql_db_utils import DBUtility
from scripts.config import PLMConf

formula_handler_obj = FormulaHandler()


class PLMHandler:
    attributeGroups = list()
    plm_token = str()

    def __init__(self):
        logger.info("PLM Handler")
        self.plm_conn = PLMUtility()
        self.plm_constants_obj = app_constants.PLMConstants()
        self.app_constants_obj = app_constants.TableName()
        self.config_constants = app_constants.ConfigConstants()

    def set_attr_config_json(self):
        try:
            db_conn = DBUtility()
            data_query = f""" Select cn.config from {self.app_constants_obj.frm_configurations} cn 
                                          where cn.is_enabled = {True} and cn.name = '{self.config_constants.attribute_file_name}' """
            flag, data = db_conn.select_mysql_table(data_query)
            if data:
                config_data = data[0] if data else dict()
                config_json = config_data.get("config", [])
                self.attributeGroups = json.loads(config_json)
        except Exception as err:
            logger.error("Unable to fetch attributes data " + str(err))
            raise (str(err))

    def search_server_formula_items(self, token, search_string, pagination_details, req_attr=True):
        """
        This method is to search for formula items from PLM based on provided search string
        """
        response = {"status": "failed"}
        try:
            logger.info("Inside search_server_formula_items")
            self.plm_token = token
            self.set_attr_config_json()
            page_number = pagination_details.get("page_number", 1)
            page_size = pagination_details.get("page_size", 10)

            url = '/itemsV2'
            params = {
                "q": f"(lower(ItemDescription) like '*{str(search_string).lower()}*' "
                     f"or lower(ItemNumber) like '*{str(search_string).lower()}*' "
                     f"or lower(LongDescription) like '*{str(search_string).lower()}*') "
                     f"AND (ItemClass in {str(tuple(PLMConf.plm_allowed_classes))}) "
                     f"AND OrganizationCode='{PLMConf.plm_org}' ",
                "onlyData": 'false',
                "limit": page_size,
                "offset": (page_number-1) * page_size,
                "fields": "ItemId,OrganizationId,OrganizationCode,ItemNumber,ItemDescription,PrimaryUOMValue,ItemClass,ItemStatusValue,ItemEffCategory,ItemRevision",
                "totalResults": 'true'
            }
            items_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            item_response = self.formula_item(items_data, req_attr)
            
            logger.info("Completed search_server_formula_items")
            response = {"status": "success", "message": "Data fetched successfully" if item_response else "No data found",
                        "data": item_response, "totalResults": items_data.get("totalResults")}
        except Exception as err:
            logger.error(f"Error while searching formula items from PLM {str(err)}")
            raise Exception(str(err))
        return response

    def formula_item(self, item_data, req_attr=True):
        """
        forming formula item with item given
        """
        try:
            item_list = list()
            att_batch_req_list = list()
            for each_item in item_data.get("items", []):
                final_item = dict()
                final_item["refId"] = each_item.get("ItemNumber", "")
                final_item["serverDbId"] = each_item.get("ItemNumber", "")
                final_item["name"] = each_item.get("ItemDescription", "")
                final_item["scrapFactor"] = self.plm_constants_obj.formula_item_scrapFactor
                final_item["percentage"] = self.plm_constants_obj.formula_item_percentage
                final_item["deleted"] = self.plm_constants_obj.formula_item_deleted
                uom = each_item.get("PrimaryUOMValue", "")
                final_item["availableUOMs"] = {
                    uom: {
                        "name": uom,
                        "category": self.plm_constants_obj.formula_item_uom_category,
                        "factor": self.plm_constants_obj.formula_item_uom_factor
                    }
                }
                final_item["baseUOM"] = uom
                final_item["selectedUOM"] = uom
                final_item["sequenceNumber"] = 0
                final_item["classType"] = self.plm_constants_obj.formula_item_classType
                final_item["itemId"] = each_item.get("ItemId", "")
                final_item["orgId"] = each_item.get("OrganizationId", "")
                latest_rev_id, latest_rev_code = self.get_latest_revision(each_item.get("ItemRevision", {}))
                final_item["revisionCode"] = latest_rev_code
                final_item["revisionId"] = latest_rev_id
                # final_item["bomId"] = ""  # TODO
                # final_item["bomType"] = ""

                final_item["attributes"] = {
                    "Revision": self.plm_constants_obj.formula_item_attributes_Revision,
                    "ItemClass": each_item.get("ItemClass", ""),
                    "ItemStatusValue": each_item.get("ItemStatusValue", ""),
                    "OrganizationCode": each_item.get("OrganizationCode", ""),
                    "ItemId": each_item.get("ItemId", "")
                }
                if req_attr:
                    self.load_attributes_requests(each_item, final_item, att_batch_req_list)
                item_list.append(final_item)
            if not att_batch_req_list:
                return item_list
            batch_response = self.plm_conn.batch_request(self.plm_token, att_batch_req_list)
            self.process_attributes(item_list, batch_response)
            return item_list
        except Exception as err:
            logger.error(f"Error in formula item {str(err)}")
            raise Exception(str(err))

    def load_attributes_requests(self, each_item, new_item, att_batch_req_list):
        """
        """
        try:
            item_eff_category = each_item.get("ItemEffCategory", {})
            if not isinstance(item_eff_category, dict):
                if isinstance(item_eff_category, str):
                    try:
                        import json
                        item_eff_category = json.loads(item_eff_category)
                        logger.warning(f"ItemEffCategory converted from string to dict: {item_eff_category}")
                    except Exception as e:
                        logger.error(f"Could not convert ItemEffCategory to dict: {item_eff_category} - Error: {e}")
                        return
                else:
                    logger.error(f"ItemEffCategory is not a dict: {item_eff_category}")
                    return
            att_links = item_eff_category.get("items", [{}])[0].get("@context", {}).get("links", [])
            valid_group_list = [each_att.get("name") for each_att in att_links]

            for each_group in self.attributeGroups:
                group_type = each_group.get("attributeGroupType")
                group_name = each_group.get("attributeGroup")
                if group_name not in valid_group_list:
                    continue
                item_id = new_item['attributes']['ItemId']
                if group_type in ["bom_header", "bom_component"]:
                    logger.info("Group not supported yet")
                elif group_type in ["item_multiline", "item_simple"]:
                    att_batch_req_list.append(
                        {
                            "id": f"{item_id}--{group_name}--{group_type}",
                            "path": f"/itemsV2/{item_id}/child/ItemEffCategory/{item_id}/child/{group_name}",
                            "operation": "get"
                        }
                    )

        except Exception as err:
            logger.error("Exception while loading attributes " + str(err))
            raise Exception(str(err))

    def process_attributes(self, item_list, batch_response):
        """
        """
        try:
            logger.info(self.__module__)
            att_json = dict()
            for each_part in batch_response.get("parts", []):
                itm_details = each_part.get("id", "").split("--")
                grp_name = itm_details[1]
                itm_id = itm_details[0]
                if itm_id not in att_json.keys():
                    att_json[itm_id] = dict()
                att_json[itm_id][grp_name] = each_part
            for each_item in item_list:
                itm_id = each_item["attributes"]["ItemId"]
                item_att_json = att_json.get(itm_id, {})
                for each_group in self.attributeGroups:
                    group_type = each_group.get("attributeGroupType")
                    group_name = each_group.get("attributeGroup")
                    if group_type not in ["item_simple", "item_multiline"]:
                        continue
                    att_data = item_att_json.get(group_name, {}).get("payload", {})
                    self.read_item_attributes(each_group, att_data, each_item, group_type == "item_multiline")
                    each_item["attributes"].pop("ItemId", None)

        except Exception as err:
            logger.error(f"Error in read item attributes {str(err)}")
            raise Exception(str(err))

    def read_item_attributes(self, each_group, att_data, new_item, is_multiline):
        """
        """
        try:
            logger.info(self.__module__)
            fields_list = [each_child_att.get("field") for each_child_att in each_group.get("children", [])]
            field_values = dict()
            if not att_data.get("items"):
                return
            if not is_multiline:
                for each_field in fields_list:
                    if str(att_data.get("items")[0].get(each_field)).lower() not in ["null", "none", ""]:
                        field_values[each_field] = str(att_data.get("items", [{}])[0].get(each_field))
            else:
                field_key = each_group.get("fieldMethod", "")
                value_key = each_group.get("valueMethod", "")
                for each_item in att_data.get("items", []):
                    if str(each_item.get(value_key, "")).lower() not in ["null", "none", ""]:
                        field_values[each_item.get(field_key, "")] = str(each_item.get(value_key, ""))

            new_item.get("attributes").update(field_values)
        except Exception as err:
            logger.error(f"Error in read item attributes {str(err)}")
            raise Exception(str(err))

    def compliance_attributes(self, root_item, comp_js):
        try:
            if not root_item.get("deleted", 0):
                attr = root_item.get("attributes", {})
                shelf_lst = []

                for rec in comp_js:
                    fld_name = rec.get("field", '')
                    if fld_name in attr:
                        continue
                    root_item["attributes"][fld_name] = "No"
                for rec in root_item.get("formula", {}).get("children", []):
                    rec_att_js = rec.get("attributes", {})
                    self.compliance_attributes(rec, comp_js)
                    if "shelfLifeDays" in rec_att_js and not rec.get("deleted", 0):
                        shelf_lst.append(float(rec_att_js["shelfLifeDays"]))
                if shelf_lst:
                    root_item['attributes']['shelfLifeDays'] = min(shelf_lst)
                if 'potencyVal' not in attr:
                    root_item['attributes']['potencyVal'] = 100
                if 'overage' not in attr:
                    root_item['attributes']['overage'] = 0
                root_item['attributes']['claimQuantity'] = root_item.get('quantity', 1.0)//((float(root_item['attributes']['potencyVal'])//100) * (1+(float(root_item['attributes']['overage'])//100)))
        except Exception as err:
            logger.error(f"Error in compliance_attributes {str(err)}")
            raise Exception(str(err))

    def assign_claim_quantity(self, root_item):
        try:
            if root_item.get("deleted", 0):
                return
            attr = root_item.get("attributes", {})
            for rec in root_item.get("formula", {}).get("children", []):
                self.assign_claim_quantity(rec)
            if 'potencyVal' not in attr:
                root_item['attributes']['potencyVal'] = 100.00000
            if 'overage' not in attr:
                root_item['attributes']['overage'] = 0.00000
            root_item['attributes']['claimQuantity'] = root_item.get('quantity', 1.0)
        except Exception as err:
            logger.error(f"Error in assign_claim_quantity {str(err)}")
            raise Exception(str(err))

    def per100g_cal(self, root_item, field):
        try:
            main_qty = 0
            # root_att_json = root_item.get("attributes", {})
            root_qty = root_item.get("quantity", 1)
            for rec in root_item.get("formula", {}).get("children", []):
                if rec.get("deleted", 0):
                    continue
                if rec.get("formula", {}).get("children", []):
                    self.per100g_cal(rec, field)
                chld_att = rec.get("attributes", {})
                qty = rec.get("quantity", 0)
                if field in chld_att and qty:
                    main_qty = main_qty + float(chld_att[field]) * qty / float(root_qty)

            # if main_qty:
            root_item['attributes'][field] = round(main_qty, 5) or main_qty
        except Exception as err:
            logger.error(f"Error in per100g_cal {str(err)}")
            raise Exception(str(err))

    def roll_up_type_min(self, root_item, field):
        try:
            value_list = list()
            for rec in root_item.get("formula", {}).get("children", []):
                if rec.get("deleted", 0):
                    continue
                rec_att_js = rec.get("attributes", {})
                self.roll_up_type_min(rec, field)
                if field in rec_att_js:
                    value_list.append(float(rec_att_js[field]))
            if value_list:
                root_item['attributes'][field] = min(value_list)
        except Exception as err:
            logger.error(f"Error in roll_up_type_min {str(err)}")
            raise Exception(str(err))

    def roll_up_type_and(self, root_item, field):
        try:
            value_list = list()
            for rec in root_item.get("formula", {}).get("children", []):
                if rec.get("deleted", 0):
                    continue
                self.roll_up_type_and(rec, field)
                rec_att_js = rec.get("attributes", {})
                if field not in rec_att_js:
                    rec["attributes"][field] = "No"
                value_list.append(rec_att_js[field])

            if value_list:
                result = "Yes" if all(val == "Yes" for val in value_list) else "No"
                root_item['attributes'][field] = result
        except Exception as err:
            logger.error(f"Error in roll_up_type_and {str(err)}")
            raise Exception(str(err))

    def calculate_attributes(self, root_item):
        try:
            quantity = sum(i.get("quantity", 0) for i in root_item.get("formula", {}).get("children", []) if
                           not (i.get("deleted")))
            self.update_percentages_to_root(root_item, quantity, 100)
            self.assign_claim_quantity(root_item)
            for rec in self.attributeGroups:
                for child in rec.get("children", []):
                    if child.get("rollupType", '') == "per100g":
                        self.per100g_cal(root_item, child.get("field", ''))
                    elif child.get("rollupType", '') == "min":
                        self.roll_up_type_min(root_item, child.get("field", ''))
                    elif child.get("rollupType", '') == "and":
                        self.roll_up_type_and(root_item, child.get("field", ''))
        except Exception as err:
            logger.error(f"Error in calculate attributes {str(err)}")
            raise Exception(str(err))

    def fetch_item(self, item_number, org):
        """
        This method is to fetch item details from PLM
        """
        response = {"status": "failed"}
        try:
            url = '/itemsV2'
            params = {
                "q": f"ItemNumber='{item_number}' AND OrganizationCode='{org}'",
                "onlyData": 'false',
                "fields": "ItemId,OrganizationId,OrganizationCode,ItemNumber,ItemDescription,PrimaryUOMValue,ItemClass,ItemStatusValue,ItemEffCategory,ItemRevision",
            }
            items_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            if not items_data.get("count", 0):
                raise Exception(f"Error while fetching PLM data")
            item_cls = items_data.get("items", [{}])[0].get("ItemClass")
            if item_cls not in PLMConf.plm_allowed_classes:
                raise ValueError(f"Error while fetching PLM data. Encountered invalid item class: '{item_cls}'")
            item_response = self.formula_item(items_data)
            response["status"] = "success"
            response["data"] = item_response
        except ValueError as err:
            raise ValueError(str(err))
        except Exception as err:
            logger.error(f"Error while fetching item from PLM {str(err)}")
            raise Exception(str(err))
        return response

    def get_server_formula_tree(self, token, username, item_number, bom='', org='', input_payload=None):
        """
        This method fetches formula tree of a specific item from PLM
        """
        if input_payload is None:
            input_payload = dict()
        response = {"status": "failed"}
        try:
            logger.info("Inside get_server_formula_tree")
            self.plm_token = token
            self.set_attr_config_json()
            op_type = input_payload.get("type", "")
            db_id = input_payload.get("db_id", "")
            root_db_id = input_payload.get("root_db_id", "")
            org = org if str(org).lower() not in ["null", "none", "undefined", ""] else PLMConf.plm_org

            logger.info("Fetching formula tree from PLM")
            # Creating data for root item
            root_item = self.fetch_item(item_number, org)
            if not root_item["data"]:
                return {}
            root_item = root_item["data"][0]
            root_item["quantity"] = 1.0
            root_item["type"] = 'output'
            root_item["formula"] = {
                "refId": item_number,
                "name": bom,
                "serverId": item_number,
                "createdDate": datetime.now().strftime("%b %d, %Y %I:%M:%S %p"),
                "attributes": {
                    "bom": bom,
                    "org": org
                }
            }
            # Recursively adding ingredient data to the root item and Calling save formula function
            if op_type in ["refreshFromPLM", "comparisonTree", "cloneServerTree"]:  # cloneServerTree is internal call from BE API copy_formula_tree_from_server
                self.recursive_tree_addition(root_item, bom, org)
                self.calculate_attributes(root_item)
                if op_type == "refreshFromPLM":
                    response = formula_handler_obj.formula_children_delete_insertion(
                        username, {"db_id": db_id, "fri_db_id": root_db_id, "data": root_item})
                    return response
            else:
                self.recursive_tree_addition(root_item, bom, org, root_item["quantity"])
            response["status"] = "success"
            response["data"] = root_item
            logger.info("Completed get_server_formula_tree")
        except (ValueError, Exception) as err:
            response["status"] = "failed"
            response["message"] = err.args[0]
        return response

    def recursive_tree_addition(self, root_item, bom, org, root_item_quan=None):
        """
        root_item: parent data
        bom: BOM
        org: organisation code
        root_item_quan: this is quantity of parent, used to assign the quantity to children rows
        parent_del: this is to delete child row if the parent row is deleted in the formula
        """
        try:
            url = '/itemStructures'
            params = {
                "q": "ItemNumber='" + root_item["refId"] + "' AND OrganizationCode='" + org + "'",
                # "q": "ItemNumber='" + root_item["refId"] + "' AND StructureName='" + bom + "' AND OrganizationCode='" + org + "'",
                "onlyData": 'true',
                "expand": "Component,Component.SubstituteComponent",
            }
            if str(bom).lower() not in ["null", "none", "undefined", ""]:
                params["q"] = params["q"] + " AND StructureName='" + bom + "'"

            structureResult = self.plm_conn.get_from_plm(self.plm_token, url, params)
            if not structureResult or structureResult.get("count") == 0:
                return
            component_list = structureResult.get("items", [{}])[0].get("Component", {}).get("items", [])
            if not component_list:
                return
            validated_component_list = self.validate_components_list_by_date(component_list)
            sorted_component_list = sorted(validated_component_list, key=lambda each: int(each.get("ItemSequenceNumber", 0)))

            if root_item_quan:
                self.update_quantity_of_children(sorted_component_list, root_item_quan)

            if "formula" not in root_item:
                formula = {
                    "refId": root_item.get("refId"),
                    "name": bom + " - " + root_item.get("refId"),
                    "createdDate": datetime.now().strftime("%b %d, %Y %I:%M:%S %p"),
                    "attributes": {},
                }
                root_item["formula"] = formula
                root_item["type"] = "output"
            root_item["formula"]["bomId"] = str(structureResult.get("items", [{}])[0].get("BillSequenceId"))
            root_item["formula"]["bomType"] = structureResult.get("items", [{}])[0].get("StructureName")

            for each_comp in sorted_component_list:
                item = self.formula_item_component(each_comp, org)
                if "children" not in root_item["formula"]:
                    root_item["formula"]["children"] = list()
                root_item["formula"]["children"].append(item)
                for each_sub in each_comp.get("SubstituteComponent", {}).get("items", []):
                    if str(each_sub.get("ACDTypeValue")).lower() == "disabled":
                        continue
                    sub_item = self.formula_item_component(each_sub, org)
                    sub_item["substituteParent"] = each_comp.get("ComponentItemId")
                    if "substitutes" not in item:
                        item["substitutes"] = list()
                    item["substitutes"].append(sub_item)
                self.recursive_tree_addition(item, bom, org, each_comp.get("Quantity"))
        except ValueError as err:
            raise ValueError(str(err))
        except Exception as err:
            logger.error(f"Error in recursive tree addition {str(err)}")
            raise Exception(str(err))

    def formula_item_component(self, item, org):
        try:
            ref_id = item.get("ComponentItemNumber") or item.get("SubstituteComponentItemNumber")
            uom = item.get("PrimaryUOMValue")
            item_details = self.fetch_item(ref_id, org)
            if not item_details["data"]:
                return {}
            new_item = {
                "refId": ref_id,
                "serverDbId": ref_id,
                "quantity": float(item.get("Quantity")),
                "scrapFactor": self.plm_constants_obj.formula_item_scrapFactor,
                "percentage": self.plm_constants_obj.formula_item_percentage,
                "deleted": self.plm_constants_obj.formula_item_deleted,
                "baseUOM": uom,
                "selectedUOM": uom,
                "availableUOMs": {
                    uom: {
                        "name": uom,
                        "category": self.plm_constants_obj.formula_item_uom_category,
                        "factor": self.plm_constants_obj.formula_item_uom_factor
                    }
                },
                "sequenceNumber": int(item.get("ItemSequenceNumber", 0)),
                "classType": self.plm_constants_obj.formula_item_classType,
                "attributes": {
                    "ItemSequenceNumber": str(item.get("ItemSequenceNumber", 0)),
                }
            }

            item_details = item_details["data"][0]
            new_item["name"] = item_details.get("name")
            new_item["revisionCode"] = item_details.get("revisionCode", "")
            new_item["revisionId"] = item_details.get("revisionId", "")
            new_item["itemId"] = item_details.get("itemId", "")
            new_item["orgId"] = item_details.get("orgId", "")
            # new_item["bomId"] = item_details.get("bomId", "")
            # new_item["bomType"] = item_details.get("bomType", "")
            new_item["attributes"].update(item_details.get("attributes"))
            return new_item
        except ValueError as err:
            raise ValueError(str(err))
        except Exception as err:
            logger.error(f"Error in formula item component {str(err)}")
            raise Exception(str(err))

    def update_quantity_of_children(self, child_components, root_item_quan):
        """
        """
        try:
            root_item_quan = float(root_item_quan)
            logger.info(self.__module__)
            old_sum = 0
            for each_child in child_components:
                old_sum += float(each_child.get("Quantity"))

            for each_child in child_components:
                perc = (float(each_child.get("Quantity")) / old_sum) * 100
                each_child["Quantity"] = round((root_item_quan * perc) / 100, 5) or (root_item_quan * perc) / 100

        except Exception as err:
            logger.error(f"Error while updating the quantities {str(err)}")

    def update_percentages_to_root(self, root_item, root_quantity, total_percent):
        """
        """
        try:
            root_quantity = float(root_quantity)
            total_percent = float(total_percent)
            for i in root_item.get("formula", {}).get("children", []):
                child_quantity = float(i.get("quantity", 0))
                self.update_percentages_to_root(i, child_quantity, child_quantity * total_percent / root_quantity)
            root_item.update({"quantity": round(root_quantity, 5) or root_quantity})
            root_item.update({"percentage": round(total_percent, 5) or total_percent})
        except Exception as err:
            logger.error(f"Error while updating the percentages {str(err)}")

    def sync_formula_tree(self, token, username, bom, org, formula_tree):
        """
        """
        try:
            logger.info("Inside sync_formula_tree")
            response = {"status": "failed"}
            self.plm_token = token
            self.sync_formula_recursion(bom, org, formula_tree)
            try:
                logger.info("calling save formula tree after sync")
                # formula_tree["formula"]["attributes"]["CurrentStatus"] = "Synced"
                formula_handler_obj.save_formula_tree_handler(username, formula_tree)
            except Exception as err:
                logger.error("Sync to PLM is success, exception while saving after sync " + str(err))
                raise Exception("Sync to PLM is success, exception while saving after sync " + str(err))
            response["status"] = "success"
            response["message"] = "Synced the formula"
            logger.info("Completed sync_formula_tree")
            return response
        except Exception as err:
            logger.error("Exception while sync of formula tree " + str(err))
            raise Exception(str(err))

    def sync_formula_recursion(self, bom, org, formula_tree):
        """
        """
        try:
            ref_id = formula_tree.get("refId")
            org = org if str(org).lower() not in ["null", "none", "undefined", ""] else PLMConf.plm_org
            url = '/itemStructures'
            params = {
                "q": "ItemNumber='" + ref_id + "' AND OrganizationCode='" + org + "'",
                "expand": "Component,Component.SubstituteComponent"
            }
            structure_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            if not structure_data.get("count"):
                structure_input = {
                    "ItemId": formula_tree.get("itemId"),
                    "ItemNumber": ref_id,
                    "OrganizationId": formula_tree.get("orgId"),
                    "AlternateBOMDesignator": bom,
                    "StructureName": bom,
                    "EffectivityControl": 1,
                    "EffectivityControlValue": "Date"
                }
                post_endpoint = "/itemStructures"
                structure = self.plm_conn.post_to_plm(self.plm_token, post_endpoint, structure_input)
            elif structure_data.get("count", 0) > 1:
                raise Exception("Many structures found for productCode=" + ref_id + " bom=" + bom + " org="
                                + org + ". Please refine your search.")
            else:
                structure = structure_data.get("items", [{}])[0]
            components = [item for item in structure.get("Component", {}).get("items", []) if
                          item.get("ImplementationDateTime") is not None and item.get("EndDateTime") is None]
            structure["Component"]["items"] = components
            componentIdToFormulaItemsMap = self.getComponentIdToFormulaItemsMap(formula_tree)
            idsOfMissingComponents = list(componentIdToFormulaItemsMap.keys())
            batch_req_list = list()
            # ''' Updating quantities '''
            self.update_quantities_for_sync(components, componentIdToFormulaItemsMap, idsOfMissingComponents, structure, batch_req_list)
            # ''' Adding components to structure which are newly added '''
            structure_copy = copy.deepcopy(structure)
            self.add_new_component_for_sync(componentIdToFormulaItemsMap, idsOfMissingComponents, structure_copy)
            # ''' Adding substitute components
            self.add_substitutes_for_sync(formula_tree, structure_copy, batch_req_list)
            self.plm_conn.batch_request(self.plm_token, batch_req_list)
        except Exception as err:
            logger.error(f"Exception while sync of formula tree {str(err)}")
            raise Exception(str(err))

    def getComponentIdToFormulaItemsMap(self, formula_tree):
        """
        """
        try:
            logger.info(self.__module__)
            componentIdToFormulaItemsMap = dict()
            if formula_tree.get("formula", {}) is not None:
                for each_child in formula_tree.get("formula", {}).get("children", []):
                    componentIdToFormulaItemsMap[each_child.get("refId")] = each_child
            return componentIdToFormulaItemsMap
        except Exception as err:
            logger.error("Exception while forming componentId to formula item map" + str(err))

    def update_quantities_for_sync(self, components, componentIdToFormulaItemsMap, idsOfMissingComponents, structure, batch_req_list):
        """
        """
        try:
            logger.info(self.__module__)
            bill_seq_id = str(structure.get('BillSequenceId'))
            for each_comp in components:
                comp_seq_id = each_comp.get('ComponentSequenceId')
                each_comp_item_num = each_comp.get("ComponentItemNumber")
                if (componentIdToFormulaItemsMap.get(each_comp_item_num, {}).get("deleted")) == 1 or each_comp_item_num not in componentIdToFormulaItemsMap.keys():
                    current_time = datetime.utcnow()
                    tomorrow_time = current_time + timedelta(days=1)
                    formatted_time = tomorrow_time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                    batch_req_list.append({
                        "id": f"updateComp--{comp_seq_id}",
                        "path": f"/itemStructures/{bill_seq_id}/"
                                f"child/Component/{comp_seq_id}",
                        "operation": "update",
                        "payload": {"EndDateTime": formatted_time, "ACDTypeValue": "Updated"}
                    })
                else:
                    child = componentIdToFormulaItemsMap.get(each_comp_item_num, {})
                    current_quantity = child.get("quantity")
                    if str(each_comp["Quantity"]) != str(current_quantity):
                        batch_req_list.append({
                            "id": f"updateComp--{comp_seq_id}",
                            "path": f"/itemStructures/{bill_seq_id}/"
                                    f"child/Component/{comp_seq_id}",
                            "operation": "update",
                            "payload": {"Quantity": current_quantity, "ACDTypeValue": "Updated"}
                        })
                if each_comp_item_num in idsOfMissingComponents:
                    idsOfMissingComponents.remove(each_comp_item_num)
        except Exception as err:
            logger.error("Error while updating quantities " + str(err))

    def add_new_component_for_sync(self, componentIdToFormulaItemsMap, idsOfMissingComponents, structure_copy):
        """
        """
        try:
            logger.debug(self.__module__)
            if not idsOfMissingComponents:
                return
            for each_id in idsOfMissingComponents:
                if componentIdToFormulaItemsMap.get(each_id, {}).get("deleted"):
                    continue
                component_item_id = componentIdToFormulaItemsMap.get(each_id, {}).get("itemId")
                post_endpoint = f"/itemStructures/{str(structure_copy.get('BillSequenceId'))}/child/Component"
                post_req_body = {
                    "ComponentItemId": component_item_id,
                    "Quantity": componentIdToFormulaItemsMap.get(each_id, {}).get("quantity"),
                }
                component_data = self.plm_conn.post_to_plm(self.plm_token, post_endpoint, post_req_body)
                if "Component" not in structure_copy:
                    structure_copy["Component"] = dict()
                    structure_copy["Component"]["items"] = list()
                structure_copy["Component"]["items"].append(component_data)
        except Exception as err:
            logger.error("Error while adding new component to the structure ", str(err))
            raise Exception(str(err))

    def add_substitutes_for_sync(self, formula_tree, structure, batch_req_list):
        """
        """
        try:
            logger.debug(self.__module__)
            bill_seq_id = str(structure.get('BillSequenceId'))
            plm_comp_sub_map = dict()
            comp_and_com_seq_map = dict()
            for each_plm_comp in structure.get("Component", []).get("items", []):
                comp_and_com_seq_map[str(each_plm_comp["ComponentItemId"])] = str(
                    each_plm_comp.get("ComponentSequenceId"))
                for each_sub_comp in each_plm_comp.get("SubstituteComponent", {}).get("items", []):
                    if str(each_sub_comp.get("ACDTypeValue")).lower() == "disabled":
                        continue
                    if each_plm_comp["ComponentItemId"] not in plm_comp_sub_map:
                        plm_comp_sub_map[each_plm_comp["ComponentItemId"]] = list()
                    plm_comp_sub_map[each_plm_comp["ComponentItemId"]].append(each_sub_comp)

            app_comp_sub_map = dict()
            for each_child in formula_tree.get("formula", {}).get("children", []):
                if not each_child.get("substitutes", []):
                    continue
                if each_child["itemId"] not in app_comp_sub_map:
                    app_comp_sub_map[each_child["itemId"]] = list()
                app_comp_sub_map[each_child["itemId"]].extend(each_child.get("substitutes", []))

            id_json = dict()
            for key, rec in app_comp_sub_map.items():
                for each_rec in rec:
                    if key not in id_json:
                        id_json[key] = dict()
                    id_json[key][str(each_rec.get("itemId", ""))] = {"quantity": each_rec.get("quantity", 1),
                                                                     "deleted": each_rec.get("deleted", 0)}
            for key, value in plm_comp_sub_map.items():
                for rec in value:
                    sub_id = str(rec.get("SubstituteComponentId", ''))
                    sub_seq_id = rec.get('SubstituteComponentSequenceId')
                    if sub_id not in id_json.get(key, {}) or id_json.get(key, {}).get(sub_id, {}).get("deleted",
                                                                                                      0) != 0:
                        batch_req_list.append({
                            "id": f"deleteSub--{sub_seq_id}",
                            "path": f"/itemStructures/{bill_seq_id}/"
                                    f"child/Component/{str(comp_and_com_seq_map.get(str(key)))}/child/SubstituteComponent/{sub_seq_id}",
                            "operation": "delete"
                        })
                        id_json.get(key, {}).pop(sub_id, None)
                        continue
                    if sub_id in id_json.get(key, {}):
                        quantity = id_json.get(key, {}).get(sub_id, {}).get("quantity", 1)
                        if str(rec.get("Quantity")) != str(quantity):
                            batch_req_list.append({
                                "id": f"updateSub--{sub_seq_id}",
                                "path": f"/itemStructures/{bill_seq_id}/"
                                        f"child/Component/{str(comp_and_com_seq_map.get(str(key)))}/child/SubstituteComponent/{sub_seq_id}",
                                "operation": "update",
                                "payload": {"Quantity": quantity, "ACDTypeValue": "Updated"}
                            })
                        id_json.get(key, {}).pop(sub_id, None)
            for id_key, id_value in id_json.items():
                for each_sub_comp in id_value:
                    if id_value.get(each_sub_comp, {}).get("deleted", 0):
                        continue
                    batch_req_list.append({
                        "id": f"addSub--{id_key}--{each_sub_comp}",
                        "path": f"/itemStructures/{bill_seq_id}/"
                                f"child/Component/{str(comp_and_com_seq_map.get(str(id_key)))}/child/SubstituteComponent",
                        "operation": "create",
                        "payload": {"Quantity": id_value.get(each_sub_comp, {}).get("quantity", 1),
                                    "SubstituteComponentId": each_sub_comp}
                    })
        except Exception as err:
            logger.error("Error while processing sub component to the structure ", str(err))
            raise Exception(str(err))

    def validate_plm_user(self, user_name, token):
        """
        """
        try:
            params = {
                "q": f"lower(Username)='{str(user_name).lower()}'"
            }
            user_data = self.plm_conn.validate_plm_user(params, token)
            if not user_data or user_data.get("count", 0) == 0 or \
                    user_data.get("count", 0) > 1 or not user_data.get("items", [])[0].get("ActiveFlag"):
                return False
            return True
        except Exception as err:
            logger.error("Error while validating user in PLM ", str(err))
            raise Exception(str(err))

    def search_server_formulas(self, token, ref_id, org, pagination_details):
        """
        This method fetches formula tree of a specific item from PLM
        """
        response = {"status": "failed"}
        try:
            logger.info("Inside search_server_formulas")
            self.plm_token = token
            page_number = pagination_details.get("page_number", 1)
            page_size = pagination_details.get("page_size", 10)
            org = org if str(org).lower() not in ["null", "none", "undefined", ""] else PLMConf.plm_org

            url = '/itemStructures'
            params = {
                "q": "ItemNumber='" + ref_id + "' AND OrganizationCode='" + org + "'",
                "onlyData": "true",
                "limit": page_size,
                "offset": (page_number-1) * page_size,
                "fields": "ItemNumber,StructureName,OrganizationCode",
                "totalResults": 'true'
            }
            structureResult = self.plm_conn.get_from_plm(self.plm_token, url, params)
            formula_list = list()
            for each_struct in structureResult.get("items", []):
                frm_dict = {
                    "refId": each_struct.get("ItemNumber"),
                    "name": each_struct.get("StructureName"),
                    "attributes": {
                        "org": each_struct.get("OrganizationCode")
                    }
                }
                formula_list.append(frm_dict)
            response["status"] = "success"
            response["data"] = formula_list
            response["message"] = "Data fetched successfully" if formula_list else "No data found"
            response["totalResults"] = structureResult.get("totalResults")
            logger.info("Completed search_server_formulas")
            return response
        except Exception as err:
            logger.error(f"Error while fetching formulas from PLM {str(err)}")
            raise Exception(str(err))

    def copy_formula_tree_from_server(self, token, username, item_number, bom, org, name):
        """
        """
        try:
            self.plm_token = token
            logger.info("Inside copy_formula_tree_from_server")
            name_status = formula_handler_obj.name_validation(name)
            if not name_status:
                return {
                    "status": "failed",
                    "message": "The formula name already exists. Please try creating it with a different name",
                    "data": {}
                }
            server_frm_tree_resp = self.get_server_formula_tree(token, username, item_number, bom, org, {"type": "cloneServerTree"})
            if not (server_frm_tree_resp or server_frm_tree_resp.get("data")):
                raise Exception("No server formula found")
            if server_frm_tree_resp.get("status") == "failed":
                return server_frm_tree_resp
            server_frm_tree = server_frm_tree_resp.get("data")
            server_frm_tree["formula"]["attributes"]["CurrentStatus"] = "Draft"
            # Calling save as function with user given to save the copied server formula
            logger.info("Calling save as Function")
            return formula_handler_obj.save_formula_tree_as(username, name, server_frm_tree, True)
        except Exception as err:
            logger.error("Exception while copying formula from server " + str(err))
            raise Exception(str(err))

    def pre_sync_formula_tree(self, token, bom, org, formula_tree):
        """
        """
        try:
            logger.info("Inside pre_sync_formula_tree")
            self.plm_token = token
            item_id = formula_tree.get("itemId", None)
            life_cycle_phase_value, revision_data = self.get_life_cycle_phase_and_revision_data(item_id, org)
            # Checking if item is in pre-production phase
            if life_cycle_phase_value in app_constants.PLMConstants.pre_production_phases:
                return {"status": "success", "syncable": True}
            # Checking if FWB item is in latest revision
            latest_rev_id, latest_rev_code = self.get_latest_revision(revision_data)
            if latest_rev_id != formula_tree.get("revisionId", None):
                return {"status": "success", "syncable": False, "type": "revisionMismatch"}
            return self.get_existing_change_orders(token, item_id, org)
        except Exception as err:
            logger.error("Exception while pre sync of formula tree " + str(err))
            raise Exception(str(err))

    def get_life_cycle_phase_and_revision_data(self, item_id, org):
        """
        """
        try:
            org = org if str(org).lower() not in ["null", "none", "undefined", ""] else PLMConf.plm_org
            url = '/itemsV2'
            params = {
                "q": f"ItemId='{item_id}' and OrganizationCode='{org}'",
                "onlyData": 'true',
                "fields": "LifecyclePhaseValue,ItemRevision",
            }
            items_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            if not items_data.get("count", 0):
                raise Exception(f"No data found for given item")
            life_cycle_phase_value = items_data.get("items", [{}])[0].get("LifecyclePhaseValue")
            revision_data = items_data.get("items", [{}])[0].get("ItemRevision", {})
            return life_cycle_phase_value, revision_data
        except Exception as err:
            logger.error(f"Error while getting life cycle phase and revision data {str(err)}")
            raise Exception(str(err))

    def get_latest_revision(self, revision_data):
        """
        """
        try:
            logger.debug(self.__module__)
            latest_revision = [item for item in revision_data.get("items", []) if item["EndEffectivityDate"] is None]
            if not latest_revision:
                raise Exception(f"No revision found for given item")
            return latest_revision[0]["RevisionId"], latest_revision[0]["RevisionCode"]
        except Exception as err:
            logger.error(f"Error while getting latest revision {str(err)}")
            raise Exception(str(err))

    def get_existing_change_orders(self, token, item_id, org, search_text=None, pagination_details=None):
        """
        """
        try:
            logger.info("Inside get_existing_change_orders")
            self.plm_token = token
            if not pagination_details:
                pagination_details = dict()
            org = org if str(org).lower() not in ["null", "none", "undefined", ""] else PLMConf.plm_org
            url = '/productChangeOrdersV2'
            params = {
                "q": f"changeOrderAffectedObject.ItemId='{item_id}' and StatusTypeValue != 'Completed' "
                     f"and StatusTypeValue != 'Canceled' and OrganizationCode = '{org}'",
                "onlyData": 'true',
                "fields": "ChangeNotice,ChangeId,ChangeName,Description,StatusTypeValue,changeOrderAffectedObject",
                "limit": pagination_details.get("page_size", 25),
                "offset": (pagination_details.get("page_number", 1) - 1) * pagination_details.get("page_size", 10),
                "totalResults": 'true',
                "orderBy": "LastUpdateDateTime:desc"
            }
            if search_text:
                search_text = str(search_text).lower()
                params["q"] = params["q"] + f" and (lower(ChangeName) like '*{search_text}*' or " \
                                            f"lower(ChangeId) like '*{search_text}*' or " \
                                            f"lower(ChangeNotice) like '*{search_text}*')"
            co_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            all_co_list = list()
            if not co_data.get("count") and not pagination_details:
                change_types = self.get_product_change_types()
                return {"status": "success", "syncable": False, "type": "createNewCo", "changeTypes": change_types}
            for each_co in co_data.get("items", []):
                each_co_details = dict()
                for each_aff_item in each_co["changeOrderAffectedObject"]["items"]:
                    if each_aff_item.get("ItemId") == item_id:
                        each_co_details["NewItemRevision"] = each_aff_item.get("NewItemRevision")
                        each_co_details["ChangeLineId"] = each_aff_item.get("ChangeLineId")
                        break
                all_co_list.append({
                    "number": each_co["ChangeNotice"],
                    "name": each_co["ChangeName"],
                    "description": each_co["Description"],
                    "status": each_co["StatusTypeValue"],
                    "itemRevision": each_co_details["NewItemRevision"],
                    "ChangeLineId": each_co_details["ChangeLineId"],
                    "changeId": each_co["ChangeId"]
                })
            
            logger.info("Completed get_existing_change_orders")
            return {"status": "success", "syncable": False, "type": "itemCOExists", "COList": all_co_list,
                    "totalResults": co_data.get("totalResults")}
        except Exception as err:
            logger.error(f"Error while getting existing change orders {str(err)}")
            raise Exception(str(err))

    def fetch_all_draft_and_open_COs(self, token, pagination_details, org, search_text, item_id):
        """
        Take pagination stuff from here
        """
        try:
            logger.info("Inside fetch_all_draft_and_open_COs")
            self.plm_token = token
            org = org if str(org).lower() not in ["null", "none", "undefined", ""] else PLMConf.plm_org
            page_number = pagination_details.get("page_number", 1)
            page_size = pagination_details.get("page_size", 10)
            url = '/productChangeOrdersV2'
            params = {
                "q": f"(StatusTypeValue = 'Open' or StatusTypeValue = 'Draft') and OrganizationCode = '{org}'",
                "onlyData": 'true',
                "limit": page_size,
                "offset": (page_number-1) * page_size,
                "totalResults": 'true',
                "orderBy": "LastUpdateDateTime:desc",
                "fields": "ChangeNotice,ChangeId,ChangeName,Description,StatusTypeValue,changeOrderAffectedObject"
            }
            if search_text:
                search_text = str(search_text).lower()
                params["q"] = params["q"] + f" and (lower(ChangeName) like '*{search_text}*' or " \
                                            f"lower(ChangeId) like '*{search_text}*' or " \
                                            f"lower(ChangeNotice) like '*{search_text}*')"
            co_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            if not co_data.get("count"):
                return {"status": "success", "message": "No open/draft change orders found", "allCOList": []}
            all_co_list = list()
            for each_co in co_data.get("items", []):
                each_co_details = dict()
                for each_aff_item in each_co["changeOrderAffectedObject"]["items"]:
                    if each_aff_item.get("ItemId") == item_id:
                        each_co_details["NewItemRevision"] = each_aff_item.get("NewItemRevision")
                        each_co_details["ChangeLineId"] = each_aff_item.get("ChangeLineId")
                        break
                all_co_list.append({
                    "number": each_co["ChangeNotice"],
                    "name": each_co["ChangeName"],
                    "description": each_co["Description"],
                    "status": each_co["StatusTypeValue"],
                    "changeId": each_co["ChangeId"],
                    "ChangeLineId": each_co_details.get("ChangeLineId"),
                    "itemRevision": each_co_details.get("NewItemRevision")
                })

            # Add available revision IDs
            existing_revisions = self.fetch_existing_revision_codes(item_id)

            logger.info("Completed fetch_all_draft_and_open_COs")
            return {"status": "success", "allCOList": all_co_list, "allRevisionCodes": existing_revisions,
                    "totalResults": co_data.get("totalResults")}
        except Exception as err:
            logger.error(f"Error while fetching all draft and open change orders {str(err)}")
            raise Exception(str(err))

    def create_change_order(self, token, username, name, desc, change_type, new_revision, org, bom, formula_tree):
        """
        """
        try:
            logger.info("Inside create_change_order")
            self.plm_token = token
            url = '/productChangeOrdersV2'
            co_input = {
                "ChangeTypeValue": change_type,
                "ChangeName": name,
                "Description": desc,
                "OrganizationCode": org,
                "changeOrderAffectedObject": [
                    {
                        "ItemNumber": formula_tree.get("refId", None),
                        "OldRevisionId": formula_tree.get("revisionId", None),
                        "NewItemRevision": new_revision
                    }
                ]
            }
            co_resp = self.plm_conn.post_to_plm(self.plm_token, url, co_input)
            change_id = co_resp.get('ChangeId')
            comp_changes_dict, bill_seq_id = self.get_changed_components(change_id, bom, org, formula_tree)
            change_line_id = co_resp.get("changeOrderAffectedObject", {}).get("items", [{}])[0].get("ChangeLineId")
            self.process_redline_components(change_id, change_line_id, comp_changes_dict, bill_seq_id)
            # Saving the formula in local
            try:
                logger.info("calling save formula tree after sync")
                formula_tree["formula"]["attributes"]["CurrentStatus"] = "Synced"
                formula_handler_obj.save_formula_tree_handler(username, formula_tree)
            except Exception as err:
                logger.error("Sync to PLM is success, exception while saving after sync " + str(err))
                raise Exception("Sync to PLM is success, exception while saving after sync " + str(err))
            logger.info("Completed create_change_order")
            return {"status": "Success", "message": "Successfully created a new change order and synced"}
        except Exception as err:
            logger.error(f"Error while creating a new change order {str(err)}")
            raise Exception(str(err))

    def increment_revision(self, rev):
        try:
            logger.debug(self.__module__)
            if not rev:
                return rev
            last_char = rev[-1]
            if last_char.isalnum():
                return rev[:-1] + chr(ord(last_char) + 1) if last_char.isalpha() else rev[:-1] + str(int(last_char) + 1)
            else:
                return rev[:-1] + chr(ord(last_char) + 1)
        except Exception as err:
            logger.error(f"Error while creating a new change order {str(err)}")
            raise Exception(str(err))

    def process_redline_components(self, change_id, change_line_id, changes_dict, bill_seq_id):
        try:
            url = '/productChangeOrdersV2'
            params = {
                "q": f"ChangeId='{change_id}'",
                "onlyData": 'true',
                "expand": "changeOrderAffectedObject.changeOrderAffectedItem,changeOrderAffectedObject.changeOrderAffectedItemStructure.affectedItemStructureComponent,changeOrderAffectedObject.changeOrderAffectedItemStructure.affectedItemStructureComponent.affectedItemSubstituteComponent",
                "links": "child"
            }
            co_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            existing_comps = list()
            for each_aff_obj in co_data["items"][0]["changeOrderAffectedObject"]["items"]:
                if each_aff_obj.get("ChangeLineId") == change_line_id:
                    existing_comps = each_aff_obj["changeOrderAffectedItemStructure"]["items"][0]["affectedItemStructureComponent"]["items"]
            base_redline_comp_url = f"/productChangeOrdersV2/{change_id}/child" \
                                    f"/changeOrderAffectedObject/{change_line_id},{change_line_id}/child" \
                                    f"/changeOrderAffectedItemStructure/{bill_seq_id}/child/affectedItemStructureComponent"
            batch_req_list = list()
            for each_add_comp in changes_dict["added"]:
                add_input = {
                    "ChangeId": change_id,
                    "ChangeLineId": change_line_id
                }
                add_input.update(each_add_comp)
                batch_req_list.append({
                    "id": f"addComp--{each_add_comp['ComponentItemId']}",
                    "path": base_redline_comp_url,
                    "operation": "create",
                    "payload": add_input
                })
            for each_edit_change in changes_dict["edited"]:
                edited_comp_id = each_edit_change["ComponentItemId"]
                for each_co_struct in existing_comps:
                    if each_co_struct.get("ComponentItemId") != edited_comp_id:
                        continue
                    edit_url = base_redline_comp_url + f"/{each_co_struct.get('ComponentSequenceId')}"
                    edit_input = {
                        "ComponentQuantity": each_edit_change["Quantity"]
                    }
                    batch_req_list.append({
                        "id": f"updateComp--{each_co_struct.get('ComponentItemId')}",
                        "path": edit_url,
                        "operation": "update",
                        "payload": edit_input
                    })
            for each_del_id in changes_dict["deleted"]:
                for each_co_struct in existing_comps:
                    if each_co_struct.get("ComponentItemId") != each_del_id:
                        continue
                    del_url = base_redline_comp_url + f"/{each_co_struct.get('ComponentSequenceId')}"
                    del_input = {
                        "ACDTypeCode": 3
                    }
                    batch_req_list.append({
                        "id": f"deleteComp--{each_co_struct.get('ComponentItemId')}",
                        "path": del_url,
                        "operation": "update",
                        "payload": del_input
                    })
            self.plm_conn.batch_request(self.plm_token, batch_req_list)

            # Performing operations for substitutes
            co_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            existing_comps = list()
            for each_aff_obj in co_data["items"][0]["changeOrderAffectedObject"]["items"]:
                if each_aff_obj.get("ChangeLineId") == change_line_id:
                    existing_comps = \
                    each_aff_obj["changeOrderAffectedItemStructure"]["items"][0]["affectedItemStructureComponent"][
                        "items"]
            base_redline_comp_url = f"/productChangeOrdersV2/{change_id}/child" \
                                    f"/changeOrderAffectedObject/{change_line_id},{change_line_id}/child" \
                                    f"/changeOrderAffectedItemStructure/{bill_seq_id}/child/affectedItemStructureComponent"
            batch_req_list = list()
            for each_sub_add_comp in changes_dict["sub_added"]:
                add_input = each_sub_add_comp["payload"]
                comp_id = each_sub_add_comp["key"]
                for each_co_struct in existing_comps:
                    if each_co_struct.get("ComponentItemId") == comp_id:
                        add_sub_redline_comp_url = base_redline_comp_url\
                                                   + f"/{each_co_struct.get('ComponentSequenceId')}/child/affectedItemSubstituteComponent"
                        batch_req_list.append({
                            "id": f"addSubComp--{comp_id}--{add_input['SubstituteComponentId']}",
                            "path": add_sub_redline_comp_url,
                            "operation": "create",
                            "payload": add_input
                        })
                        break
            for each_sub_edit_change in changes_dict["sub_edited"]:
                edited_comp_id = each_sub_edit_change["key"].split("---")[0]
                edited_sub_id = each_sub_edit_change["key"].split("---")[1]
                for each_co_struct in existing_comps:
                    if each_co_struct.get("ComponentItemId") != edited_comp_id:
                        continue
                    for each_sub in each_co_struct.get("affectedItemSubstituteComponent", {}).get("items", []):
                        if each_sub.get("SubstituteComponentId") != edited_sub_id:
                            continue
                        edit_url = base_redline_comp_url + f"/{each_co_struct.get('ComponentSequenceId')}/child" \
                                                           f"/affectedItemSubstituteComponent/{each_sub.get('SubstituteComponentSequenceId')}"
                        edit_input = each_sub_edit_change["payload"]
                        batch_req_list.append({
                            "id": f"updateSubComp--{edited_comp_id}--{edited_sub_id}",
                            "path": edit_url,
                            "operation": "update",
                            "payload": edit_input
                        })
                        break
                    break
            for each_sub_del_comp in changes_dict["sub_deleted"]:
                del_comp_id = each_sub_del_comp["key"].split("---")[0]
                del_sub_id = each_sub_del_comp["key"].split("---")[1]
                for each_co_struct in existing_comps:
                    if each_co_struct.get("ComponentItemId") != del_comp_id:
                        continue
                    for each_sub in each_co_struct.get("affectedItemSubstituteComponent", {}).get("items", []):
                        if each_sub.get("SubstituteComponentId") != del_sub_id:
                            continue
                        del_url = base_redline_comp_url + f"/{each_co_struct.get('ComponentSequenceId')}/" \
                                                          f"child/affectedItemSubstituteComponent/{each_sub.get('SubstituteComponentSequenceId')}"
                        del_input = {
                            "ACDType": 3
                        }
                        batch_req_list.append({
                            "id": f"deleteSubComp--{del_comp_id}--{del_sub_id}",
                            "path": del_url,
                            "operation": "delete"
                            # "payload": del_input
                        })
                        break
                    break
            self.plm_conn.batch_request(self.plm_token, batch_req_list)
        except Exception as err:
            logger.error(f"Error while processing redline components {str(err)}")
            raise Exception(str(err))

    def get_changed_components(self, change_id, bom, org, formula_tree):
        """
        """
        try:
            ref_id = formula_tree.get("refId")
            org = org if str(org).lower() not in ["null", "none", "undefined", ""] else PLMConf.plm_org
            url = '/itemStructures'
            params = {
                "q": f"ItemNumber='{ref_id}' and OrganizationCode='{org}'",
                "expand": "Component,Component.SubstituteComponent"
            }
            structure_data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            if not structure_data.get("count"):
                raise Exception("Item structure not found")
            elif structure_data.get("count", 0) > 1:
                raise Exception("Many structures found for productCode=" + ref_id + " bom=" + bom + " org="
                                + org)
            else:
                structure = structure_data.get("items", [{}])[0]
            bill_seq_id = structure.get("BillSequenceId")
            components = [item for item in structure.get("Component", {}).get("items", []) if
                          item.get("ImplementationDateTime") is not None and item.get("EndDateTime") is None]
            structure["Component"]["items"] = components
            componentIdToFormulaItemsMap = self.getComponentIdToFormulaItemsMap(formula_tree)
            idsOfMissingComponents = list(componentIdToFormulaItemsMap.keys())
            changes_dict = {
                "added": [], "edited": [], "deleted": [], "sub_added": [], "sub_edited": [], "sub_deleted": []
            }
            self.get_changed_comps_list(components, componentIdToFormulaItemsMap, idsOfMissingComponents, changes_dict)
            # Adding substitute components
            self.get_changed_substitutes_list(formula_tree, structure, changes_dict)
            return changes_dict, bill_seq_id
        except Exception as err:
            logger.error(f"Exception while sync of formula tree {str(err)}")
            raise Exception(str(err))

    def get_changed_comps_list(self, components, componentIdToFormulaItemsMap, idsOfMissingComponents, changes_dict):
        """
        """
        try:
            logger.info(self.__module__)
            for each_comp in components:
                each_comp_item_num = each_comp.get("ComponentItemNumber")
                each_comp_item_id = componentIdToFormulaItemsMap.get(each_comp_item_num, {}).get("itemId")
                if (componentIdToFormulaItemsMap.get(each_comp_item_num, {}).get("deleted")) == 1:
                    changes_dict["deleted"].append(each_comp_item_id)
                else:
                    child = componentIdToFormulaItemsMap.get(each_comp_item_num, {})
                    current_quantity = child.get("quantity")
                    if str(each_comp["Quantity"]) != str(current_quantity):
                        changes_dict["edited"].append({"ComponentItemId": each_comp_item_id,
                                                       "Quantity": current_quantity})
                if each_comp_item_num in idsOfMissingComponents:
                    idsOfMissingComponents.remove(each_comp_item_num)
            if not idsOfMissingComponents:
                return
            for each_id in idsOfMissingComponents:
                if componentIdToFormulaItemsMap.get(each_id, {}).get("deleted"):
                    continue
                component_item_id = componentIdToFormulaItemsMap.get(each_id, {}).get("itemId")
                changes_dict["added"].append({"ComponentItemId": component_item_id,
                                              "ComponentQuantity": componentIdToFormulaItemsMap.get(each_id, {}).get("quantity"),
                                              "PrimaryUomCode": componentIdToFormulaItemsMap.get(each_id, {}).get("baseUOM")})
        except Exception as err:
            logger.error("Error while fetching component changes list " + str(err))
            raise Exception(str(err))

    def get_changed_substitutes_list(self, formula_tree, structure, changes_dict):
        """
        """
        try:
            logger.debug(self.__module__)
            plm_comp_sub_map = dict()
            for each_plm_comp in structure.get("Component", []).get("items", []):
                for each_sub_comp in each_plm_comp.get("SubstituteComponent", {}).get("items", []):
                    if str(each_sub_comp.get("ACDTypeValue")).lower() == "disabled":
                        continue
                    if each_plm_comp["ComponentItemId"] not in plm_comp_sub_map:
                        plm_comp_sub_map[each_plm_comp["ComponentItemId"]] = list()
                    plm_comp_sub_map[each_plm_comp["ComponentItemId"]].append(each_sub_comp)

            app_comp_sub_map = dict()
            for each_child in formula_tree.get("formula", {}).get("children", []):
                if not each_child.get("substitutes", []):  # or each_child.get("deleted", 0) == 1
                    continue
                if each_child["itemId"] not in app_comp_sub_map:
                    app_comp_sub_map[each_child["itemId"]] = list()
                app_comp_sub_map[each_child["itemId"]].extend(each_child.get("substitutes", []))

            id_json = dict()
            for key, rec in app_comp_sub_map.items():
                for each_rec in rec:
                    if key not in id_json:
                        id_json[key] = dict()
                    id_json[key][str(each_rec.get("itemId", ""))] = {"quantity": each_rec.get("quantity", 1),
                                                                     "deleted": each_rec.get("deleted", 0)}
            for key, value in plm_comp_sub_map.items():
                for rec in value:
                    sub_id = str(rec.get("SubstituteComponentId", ''))
                    # sub_seq_id = rec.get('SubstituteComponentSequenceId')
                    if sub_id not in id_json.get(key, {}) or id_json.get(key, {}).get(sub_id, {}).get("deleted",
                                                                                                      0) != 0:
                        changes_dict["sub_deleted"].append({"key": f"{str(key)}---{sub_id}"})
                        id_json.get(key, {}).pop(sub_id, None)
                        continue
                    if sub_id in id_json.get(key, {}):
                        quantity = id_json.get(key, {}).get(sub_id, {}).get("quantity", 1)
                        if str(rec.get("Quantity")) != str(quantity):
                            changes_dict["sub_edited"].append(
                                {"key": f"{str(key)}---{sub_id}", "payload": {"Quantity": quantity}})
                        id_json.get(key, {}).pop(sub_id, None)
            for id_key, id_value in id_json.items():
                for each_sub_comp in id_value:
                    if id_value.get(each_sub_comp, {}).get("deleted", 0):
                        continue
                    changes_dict["sub_added"].append(
                        {"key": f"{str(id_key)}",
                         "payload": {"Quantity": id_value.get(each_sub_comp, {}).get("quantity", 1),
                                     "SubstituteComponentId": each_sub_comp}})
        except Exception as err:
            logger.error("Error while getting changes in sub component to the structure ", str(err))
            raise Exception(str(err))

    def validate_components_list_by_date(self, components_list):
        try:
            logger.debug(self.__module__)
            validated_list = list()

            for each_comp in components_list:
                if each_comp.get('EndDateTime', None) in [None, "null"] and each_comp.get('ImplementationDateTime', None) not in [None, "null"]:
                    validated_list.append(each_comp)

            return validated_list
        except Exception as err:
            logger.error(f"Error while validating components list by date: {str(err)}")
            raise Exception(str(err))

    def get_product_change_types(self):
        """
            Fetches a list of values for Product Change Types
        """
        try:
            result = list()
            url = '/productChangeTypes'
            params = {
                "q": "EndDate is null",
                "onlyData": 'true',
                "fields": "InternalName,Name",
            }

            prod_change_types = self.plm_conn.get_from_plm(self.plm_token, url, params).get("items", [])

            for prod in prod_change_types:
                res = {
                    "key": prod.get("InternalName", ""),
                    "value": prod.get("Name", "")
                }
                result.append(res)

            # response = {"status": "success", "message": "Change types fetched successfully", "data": result}
            return result

        except Exception as err:
            logger.error(f"Error while creating a new change order {str(err)}")
            raise Exception(str(err))
    
    def fetch_existing_revision_codes(self, item_id):
        try:
            result = list()
            url = '/productChangeOrdersV2'
            params = {
                "q": f"changeOrderAffectedObject.ItemId='{item_id}'",
                "onlyData": 'true',
                "expand": "changeOrderAffectedObject",
                "fields": "changeOrderAffectedObject,ChangeId,ChangeName"
            }

            data = self.plm_conn.get_from_plm(self.plm_token, url, params)
            change_order_data = data.get("items", [])

            if not change_order_data:
                return result
            for co in change_order_data:
                for each_item in co.get("changeOrderAffectedObject", {}).get("items", []):
                    if each_item.get("ItemId") == item_id:
                        result.append(each_item.get("NewItemRevision", ""))
                        break

            return result
        except Exception as err:
            logger.error(f"Error while fetching existing revision codes: {str(err)}")
            raise Exception(str(err))

    def sync_with_change_order(self, token, username, bom, org, new_revision, co_details, formula_tree):
        """
        """
        try:
            logger.info("Inside sync_with_change_order")
            self.plm_token = token
            change_id = co_details.get('changeId')
            change_line_id = co_details.get('ChangeLineId')
            item_id = formula_tree.get("itemId")
            batch_list = list()
            batch_index = 0
            if not change_line_id:
                add_affect_obj_input = {
                    "ItemId": item_id,
                    "OldRevisionId": formula_tree.get("revisionId"),
                    "NewItemRevision": new_revision
                }
            else:
                batch_list.append({
                    "id": f"deleteObj--{change_line_id}",
                    "path": f"/productChangeOrdersV2/{change_id}/child/"
                            f"changeOrderAffectedObject/{change_line_id},{change_line_id}",
                    "operation": "delete"
                })
                batch_index = 1
                add_affect_obj_input = {
                    "ItemId": item_id,
                    "OldRevisionId": formula_tree.get("revisionId"),
                    "NewItemRevision": co_details.get('itemRevision')
                }
            batch_list.append({
                "id": f"addObj--{item_id}",
                "path": f"/productChangeOrdersV2/{change_id}/child/changeOrderAffectedObject",
                "operation": "create",
                "payload": add_affect_obj_input
            })
            batch_response = self.plm_conn.batch_request(self.plm_token, batch_list)
            change_line_id = batch_response["parts"][batch_index].get("payload", {}).get('ChangeLineId')
            changes_dict, bill_seq_id = self.get_changed_components(change_id, bom, org, formula_tree)
            self.process_redline_components(change_id, change_line_id, changes_dict, bill_seq_id)
            # Saving the formula in local
            try:
                logger.info("calling save formula tree after sync")
                formula_tree["formula"]["attributes"]["CurrentStatus"] = "Synced"
                formula_handler_obj.save_formula_tree_handler(username, formula_tree)
            except Exception as err:
                logger.error("Sync to PLM is success, exception while saving after sync " + str(err))
                raise Exception("Sync to PLM is success, exception while saving after sync " + str(err))
            return {"status": "success", "message": "Synced the formula"}
        except Exception as err:
            logger.error("Exception while sync of formula tree " + str(err))
            raise Exception(str(err))
    
    def getItemIdToQtyMap(self, formula_tree):
        """
            Create a mapping with Item id to qty and deleted flag from formula tree json data
        """
        try:
            logger.info(self.__module__)
            itemIdToQtyMap = dict()
            if formula_tree.get("formula", {}) is not None:
                for each_child in formula_tree.get("formula", {}).get("children", []):
                    itemIdToQtyMap[each_child.get("itemId")] = each_child.get("quantity", "")
                    item_id = each_child.get("itemId")
                    itemIdToQtyMap.update({
                        item_id: {
                            "qty": each_child.get("quantity", ""),
                            "deleted": each_child.get("deleted", ""),
                        }
                    })
            return itemIdToQtyMap
        except Exception as err:
            logger.error("Exception while forming componentId to formula item map" + str(err))

    def get_changed_components_details(self, token, change_notice, formula_tree):
        try:
            self.plm_token = token
            result = {
                "added": [],
                "deleted": [],
                "edited": []
            }
            url = '/productChangeOrdersV2'
            cn_param = f"""ChangeNotice='{change_notice}'"""
            params = {
                "q": cn_param,
                "onlyData": 'true',
                "expand": "changeOrderAffectedObject.changeOrderAffectedItem,changeOrderAffectedObject.changeOrderAffectedItemStructure.affectedItemStructureComponent"
                # "fields": "changeOrderAffectedObject,ChangeId,ChangeName"
            }

            data = self.plm_conn.get_from_plm(self.plm_token, url, params).get("items", [])[0]
            cn_data = list()
            for each_aff_obj in data.get("changeOrderAffectedObject", {}).get("items", []):
                if each_aff_obj.get("ItemId") == formula_tree.get("itemId"):
                    cn_data = each_aff_obj.get("changeOrderAffectedItemStructure", {}).get("items", [])[0].get(
                        "affectedItemStructureComponent", {}).get("items", [])
                    break

            # Map data with component ID
            mapped_cn_data = dict()
            for item in cn_data:
                mapped_cn_data.update({
                    item.get("ComponentItemId", ""): {
                        "qty": item.get("ComponentQuantity", ""),
                        "type_code": item.get("ACDTypeCode", "")
                    }})
            mapped_form_tree_data = self.getItemIdToQtyMap(formula_tree)

            for item_id, item_val in mapped_form_tree_data.items():
                if not mapped_cn_data.get(item_id):
                    result["added"].append({
                        "ComponentItemId": item_id,
                        "Quantity": item_val.get("qty")
                    })

                elif item_val.get("deleted") == 1:
                    if mapped_cn_data.get(item_id, {}).get("type_code") != 3:
                        result["deleted"].append(item_id)

                elif str(item_val.get("qty")) != str(mapped_cn_data.get(item_id, {}).get("qty")):
                    if mapped_cn_data.get(item_id, {}).get("type_code") != 3:
                        result["edited"].append({"ComponentItemId": item_id,
                                                 "Quantity": item_val.get("qty")})
                    else:
                        raise Exception("Cannot edit a deleted component")
            return result
        except Exception as err:
            logger.error(f"Error while fetching changed components details: {str(err)}")
            raise Exception(str(err))
