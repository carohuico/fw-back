class TableName:
    frm_users = "frm_users"
    frm_formula = "frm_formula"
    frm_formula_item = "frm_formula_item"
    frm_attribute_def = "frm_attribute_def"
    frm_fitem_attr_val = "frm_fitem_attr_val"
    frm_formula_attributes = "frm_formula_attributes"
    frm_uom = "frm_uom"
    frm_fitem_alt_uom = "frm_fitem_alt_uom"
    frm_user_roles = "frm_user_roles"
    frm_feature_access = "frm_feature_access"
    frm_comp_project = "frm_comp_project"
    frm_comp_local_formulas = "frm_comp_local_formulas"
    frm_comp_server_formulas = "frm_comp_server_formulas"
    frm_notes = "frm_notes"
    frm_configurations = "frm_attr_configurations"
    frm_shared_users = "frm_shared_users"
    frm_excel_configurations = "frm_excel_configurations"

class SideMenu:
    side_menu = {}


class ResponseMessage:
    @staticmethod
    def final_json(status, message, data=None, error=None):
        if data is not None and error is not None:
            return {"status": status, "message": message, "data": data, "error": error}
        elif data is not None:
            return {"status": status, "message": message, "data": data}
        elif error is not None:
            return {"status": status, "message": message, "error": error}
        else:
            return {"status": status, "message": message}


class Message:
    success = "success"
    failed = "failed"


class AESKey:
    key = "QVY1bWdMQ0Zxc"


class CommonHeaders:
    common_headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }


class UserManagement:
    list_users_header = {
        "status": "success",
        "message": "success",
        "data": {
            "showActionsLabel": True,
            "tableData": {
                "headerContent": [
                    {
                        "label": "First Name",
                        "value": "first_name"
                    },
                    {
                        "label": "Designation",
                        "value": "designation"
                    },
                    {
                        "label": "Email",
                        "value": "email"
                    },
                    {
                        "label": "Mobile",
                        "value": "mobile"
                    },
                    {
                        "label": "User Role",
                        "value": "user_role_name"
                    }
                ],
                "bodyContent": []
            },
            "tableActions": {
                "enableActions": True,
                "actions": [
                    {
                        "action": "edit",
                        "label": "Edit",
                        "type": "button",
                        "icon-class": "fa-edit"
                    },
                    {
                        "action": "delete",
                        "label": "Delete",
                        "type": "button",
                        "icon-class": "fa-trash"
                    }
                ],
                "externalActions": []
            },
            "enableActions": True,
            "rowClick": True,
            "enable_sort": True,
            "total_no": 4,
            "endOfRecords": True,
            "counter": 1,
            "table_type": "infinite_scroll",
            "server_search": True
        }
    }


class HomePage:
    development_formulae_response = {
        "status": "",
        "message": "",
        "data": []
    }

    comparison_projects_response = {
        "status": "",
        "message": "",
        "data": []
    }

    shared_formulae_response = {
        "status": "",
        "message": "",
        "data": []
    }


class TableIdPrefix:
    frm_formula = "frm"
    frm_formula_item = "fri"
    frm_attribute_def = "fad"
    frm_fitem_attr_val = "fav"
    frm_uom = "fum"
    frm_fitem_alt_uom = "fau"
    frm_formula_attributes = "ffa"
    frm_user_roles = "fur"
    frm_feature_access = "acc"
    frm_users = "usr"
    frm_notes = "fnt"
    frm_configurations = "fcn"
    frm_comp_project = "fcp"
    frm_excel_configs = "fec"


class PLMConstants:
    formula_item_scrapFactor = 0.0
    formula_item_percentage = 0.0
    formula_item_deleted = 0
    formula_item_uom_category = "unknown"
    formula_item_uom_factor = 1.0
    formula_item_classType = "test1"
    formula_item_attributes_Revision = "A"
    plm_rest_version = "9"
    pre_production_phases = ["Production RS", "Prototype", "Design"]


class Attributes:
    attribute_definitions = {
        "AttributeDef1": ["class1", "class2"],
        "AttributeDef2": ["class3", "class4"],
        "AttributeDef3": ["class5", "class6"]
    }


class QueryStatements:
    query_statement_dict = {
        "frm_formula_item_update": f"update {TableName.frm_formula_item} set quantity = %s, pct_scrap_factor "
                                   f"= %s, is_deleted=%s, pct_composition=%s, last_modified_date=%s, "
                                   f"last_modified_by=%s, fk_produced_by_formula = %s where id = %s",
        "frm_fitem_attr_val_update": f"update {TableName.frm_fitem_attr_val} set value_string = %s where "
                                     f"FK_ATTRIBUTE_DEF = %s and FK_FORMULA_ITEM = %s",
        "frm_attribute_def_insert": f"insert into {TableName.frm_attribute_def}(ID, NAME, TYPE, UI_WIDTH, "
                                    f"UI_HIDE_DEFAULT, UI_EDITABLE, IS_ENABLED) values(%s, %s,%s, %s, %s, %s, "
                                    f"%s)",
        "frm_fitem_attr_val_insert": f"insert into {TableName.frm_fitem_attr_val}(ID, VALUE_STRING, "
                                     f"FK_FORMULA_ITEM, FK_ATTRIBUTE_DEF) values(%s, %s, %s, %s)",
        "frm_formula_attributes_update": f"update {TableName.frm_formula_attributes} set value= %s where "
                                         f"attribute = %s and fk_formula = %s",
        "frm_formula_update": f"update {TableName.frm_formula} set LAST_MODIFIED_DATE=%s, last_modified_by=%s, "
                              f"is_editable=%s where id = %s",
        "frm_formula_item_insert": f"""insert into {TableName.frm_formula_item}(id, name, fk_formula, 
                                                quantity, fk_uom, pct_scrap_factor, is_deleted, material_ref, 
                                                item_type, pct_composition, ref_id, fk_produced_by_formula, 
                                                sequence_number, food_contact, class_type, fk_selected_uom,
                                                last_modified_date, created_date, created_by, last_modified_by,
                                                revision_code, revision_id, item_id, org_id, substitute_parent) 
                                                values(%(id)s,%(name)s,%(fk_formula)s, 
                                                %(quantity)s,%(fk_uom)s,%(pct_scrap_factor)s,%(is_deleted)s,%(material_ref)s,
                                                %(item_type)s,%(pct_composition)s,%(ref_id)s,
                                                %(fk_produced_by_formula)s,%(sequence_number)s,%(food_contact)s,
                                                %(class_type)s,%(fk_selected_uom)s, %(last_modified_date)s,
                                                %(created_date)s,%(created_by)s, %(last_modified_by)s, 
                                                %(revision_code)s, %(revision_id)s, %(item_id)s, %(org_id)s, %(substitute_parent)s)""",
        "frm_fitem_alt_uom_insertion": f"""insert into {TableName.frm_fitem_alt_uom}(id, fk_formula_item, 
                                                        fk_alternate_uom, factor) values(%(id)s, %(fk_formula_item)s, 
                                                        %(fk_alternate_uom)s, %(factor)s)""",
        "frm_uom_insertion": f"""insert into {TableName.frm_uom}(id, name, abbreviation, base_uom, 
                                            conversion, category) values(%(id)s,%(name)s,%(abbreviation)s,
                                            %(base_uom)s,%(conversion)s,%(category)s)""",
        "frm_formula_insertion": f"""insert into {TableName.frm_formula}(id, name, created_date, created_by, 
                                                fk_formula_item_output, ref_id, last_modified_date, server_id,
                                                is_editable, item_id, org_id, revision_id, revision_code,
                                                bom_id, bom_type, last_modified_by) 
                                                values(%(id)s,%(name)s,%(created_date)s, %(created_by)s, 
                                                %(fk_formula_item_output)s,%(ref_id)s,%(last_modified_date)s,
                                                %(server_id)s, %(is_editable)s, %(item_id)s, %(org_id)s,
                                                %(revision_id)s, %(revision_code)s, %(bom_id)s, %(bom_type)s,
                                                %(last_modified_by)s)""",
        "frm_formula_attributes_insertion": f"""insert into {TableName.frm_formula_attributes}(fk_formula, 
                                                            attribute, value) values(%(fk_formula)s,
                                                            %(attribute)s, %(value)s) """,
        "frm_formula_item_delete": f"""delete from {TableName.frm_formula_item} where id = %s""",
        "frm_fitem_alt_uom_delete": f"""delete from {TableName.frm_fitem_alt_uom} 
                                                    where fk_formula_item = %s""",
        "frm_uom_delete": f"""delete from {TableName.frm_uom} where id = %s""",
        "frm_fitem_attr_val_delete": f"""delete from {TableName.frm_fitem_attr_val} 
                                                    where fk_formula_item = %s""",
        "frm_attribute_def_delete": f"""delete from {TableName.frm_attribute_def} where id = %s""",
        "frm_formula_delete": f"""delete from {TableName.frm_formula} where id =%s""",
        "frm_formula_attributes_delete": f"""delete from {TableName.frm_formula_attributes} 
                                                    where fk_formula = %s"""

    }


class FormulaComparisonConstants:
    workers_count = 5
    decimal_precision = 5
    bomname_list = [
        {
            "id": "Engineering BOM",
            "value": "Engineering BOM"
        },
        {
            "id": "Manufacturing BOM",
            "value": "Manufacturing BOM"
        },
        {
            "id": "Primary",
            "value": "Primary"
        },
        {
            "id": "Production",
            "value": "Production"
        },
        {
            "id": "Engineering",
            "value": "Engineering"
        },

        {
            "id": "Design",
            "value": "Design"
        },
        {
            "id": "Planning",
            "value": "Planning"
        },
        {
            "id": "Structure",
            "value": "Structure"
        },
        {
            "id": "Sales_Bundle",
            "value": "Sales Bundle"
        }

    ]
    header_children = [
        {
            "key": "quantity",
            "label": "Quantity",
            "hide": False
        },
        {
            "key": "uom",
            "label": "UOM",
            "hide": False
        }
    ]


class ChildrenConfigs:
    enableGrndChldOps = False


class ConfigConstants:
    attribute_file_name = "attributes"
    excel_file_name = "excel"
