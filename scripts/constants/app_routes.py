class RouteTags:
    login = "Login"
    user = "User Management"
    plm = "PLM"
    role = "Role Management"


class EndPoints:
    app_base_url = "/formulation_tool"

    # Login
    api_login = "/login"
    api_get_token = "/get_token"
    api_logout = "/logout"
    api_aad_login_uri = "/aad/login_uri"
    api_aad_login = "/aad/login"
    api_saml_verify = "/saml/verify"
    api_saml_login = "/saml/login"
    api_saml_logout = "/saml/logout"
    api_saml_test_verify = "/saml/test/verify"
    forgot_password = "/user/forgot_password"
    update_password = "/user/update_password"
    reset_password = "/user/reset_password"
    send_external_image = "/send_external_image"
    check_login = "/login-check"
    verify_mfa = "/verify_mfa"

    search_server_formula_items = "/search_server_formula_items"
    get_server_formula_tree = "/get_server_formula_tree"
    sync_server_formula_tree = "/sync_server_formula_tree/{db_id}/{bom}/{org}"
    search_server_formulas = "/SearchServerFormulas"
    copy_formula_tree_from_server = "/CopyFormulaTreeFromServer"
    pre_sync_server_formula_tree = "/pre_sync_server_formula_tree/{bom}/{org}"
    create_change_order = "/create_change_order"
    get_all_draft_and_open_COs = "/fetch_all_draft_and_open_COs"
    fetch_existing_item_COs = "/fetch_existing_item_COs"
    sync_with_change_order = "/sync_with_change_order"


class UserURL:
    create_user = '/createUser'
    delete_user = '/deleteUser'
    fetch_users = '/fetchUsers'
    edit_user = '/editUser'


class HomePage:
    # Homepage
    fetch_development_formulae = "/fetchDevelopmentFormulae"
    fetch_formula_comparison_projects = "/fetchFormulaComparisonProjects"
    fetch_shared_forumalae = "/fetchSharedFormulae"
    name_details = "/fetchDraftFormulas"
    delete_compairson_project = "/deleteComparisonProject/{comp_id}"
    create_formula = "/CreateFormula"
    delete_development_formulae = "/deleteDevelopmentFormula"
    update_formula_status = "/UpdateFormulaStatus"


class Formula:
    get_local_formula_tree = "/GetLocalFormulaTree/{id}"
    save_formula_tree = "/SaveFormulaTree"
    save_formula_tree_as = "/SaveFormulaTreeAs"
    get_entry = "/getEntrys/{db_id}"
    post_entry = "/postEntry/{formula_id}"
    manage_shared_access = "/ManageSharedAccess"
    fetch_username_data = "/FetchUsernameData"
    fetch_access_info = "/FetchAccessInfo"
    get_excel_report = '/GetExcelReport'


class FormulaComparisonProject:
    get_formula_comparison_project_tree = "/GetFormulasComparisonProjectTree"
    search_local_formulas = "/SearchLocalFormulasForItem"
    create_formula_comparison_project = "/CreateFormulaComparisonProject"
    save_formula_comparison_project = "/SaveFormulaComparisonProject"
    save_as_formula_comparison_project = "/SaveAsFormulaComparisonProject"
    get_configuration = "/GetConfiguration"

class Methods:
    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    DELETE = "DELETE"


class RoleURL:
    fetch_roles = '/fetchUserRoles'
    fetch_label = '/fetchUserLabel'
    fetch_access = '/fetchUserAccess'
    create_UserRole = '/createUserRoles'
    edit_UserRole = '/editUserRole'
    fetch_UserRole_List = '/fetchUserRoleList'
    fetch_access_features = '/fetchAccessFeatures'


class TableConfig:
    get_attribute_definitions = "/GetAttributeDefinitions"
    upload_config_json = "/UploadConfigJson"
    upload_config_record = "/UploadConfigRecord"
    download_config_json = "/DownloadConfigJson"
    fetch_download_json_data = "/FetchDownloadJsonData"
    add_excel_conf_name = "/AddExcelConfName"
    fetch_excel_config = "/FetchExcelConfigs"
    delete_excel_config = "/DeleteExcelConfigs"
