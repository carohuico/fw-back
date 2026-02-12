from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    user_id: Optional[str]
    username: str
    email: str
    password: Optional[str]
    created_by: Optional[str]
    hmi: Optional[Dict] = {}
    project_id: Optional[str]
    AccessLevel: Optional[Dict] = {}
    access_group_ids: Optional[List] = []
    landing_page: Optional[str]
    name: str
    phonenumber: Optional[List] = []
    user_access_select_all: Optional[bool]
    user_type: Optional[str] = ""
    userrole: Optional[List] = []
    is_app_user: Optional[bool]
    product_access: Optional[List] = []
    location: Optional[str] = ""
    department: Optional[str] = ""
    section: Optional[str] = ""
    azure_id: Optional[str] = ""
    token_azure: Optional[str] = ""
    expires_on: Optional[str] = ""
    disable_user: Optional[bool] = False
    failed_attempts: Optional[int] = 0
    access_level_list: Optional[dict] = {}
    created_on: Optional[int]
    updated_by: Optional[str] = ""
    updated_on: Optional[int]
    mfa_enabled: Optional[bool] = False
    mfa_configured: Optional[bool] = False
    mfa_enabled_on: Optional[int]
    password_added_on: Optional[int]
    default_project: Optional[str] = None
    shift_details: Optional[dict] = {}
    shift_enabled: Optional[bool] = False


class AddExistingUser(BaseModel):
    project_id: str
    AccessLevel: Optional[Dict] = {}
    access_group_ids: Optional[List] = []
    landing_page: Optional[str]
    userrole: Optional[List] = []
    is_app_user: Optional[bool]
    product_access: Optional[List] = []
    app_url: Optional[str]
    created_by: Optional[str]
    updated_time: Optional[str]
    location: Optional[str] = ""
    department: Optional[str] = ""
    section: Optional[str] = ""
    existingUser: Optional[str] = ""
    user_id: Optional[str] = ""
    access_level_list: Optional[dict] = {}
    updated_by: Optional[str] = ""
    default_project: Optional[str] = None


class CreateAccessGroupRequest(BaseModel):
    access_group: Optional[str]
    access_group_id: str = ""
    access_list: Optional[List] = []
    description: Optional[str]
    mes_type: Optional[Any]
    project_id: Optional[str]


class TableData(BaseModel):
    bodyContent: List = []
    headerContent: List = []


class TableAction(BaseModel):
    actions: Optional[List] = []
    enableActions: Optional[bool] = True
    externalActions: Optional[List] = []


class ListBaseResponse(BaseModel):
    tableActions: Dict = TableAction()
    tableData: Dict = TableData()
    status: str = "failed"
    message: str = "Failed to fetch users list!"


class ListUserRequest(BaseModel):
    project_id: Optional[str]
    user_role_id: Optional[str]
    product_access: Optional[List] = []
    filters: Optional[Dict] = {}
    page: Optional[int]
    records: Optional[int]
    tz: Optional[str]
    user_id: Optional[str]


class SaveUserAccess(BaseModel):
    project_id: Optional[str]
    access_group_id: Optional[str]


class RoleAccessList(BaseModel):
    userroles: List = []
    accessgroups: List = []


class DeleteAccessGroupRequest(BaseModel):
    access_group_id: str


class CreateUserRole(BaseModel):
    type: str
    user_role_id: Optional[str] = ""
    access_levels: Optional[Dict] = {}
    permissionStatus: Optional[bool]
    project_id: Optional[str]
    user_role_description: Optional[str]
    user_role_id: Optional[str]
    user_role_name: Optional[str]
    user_role_permissions: Optional[Dict] = {}
    parameterRepresentation: Optional[str]
    catalogPermission: Optional[bool]
    userRolePreferenceStatus: Optional[bool] = False


class DeleteUserRole(BaseModel):
    user_role_id: str


class UserDetailRequest(BaseModel):
    user_id: str
    project_id: Optional[str]


class SaveTimezoneRequest(BaseModel):
    tz: str
    date_format: str
    time_format: str
    date_time_format: str


class DownloadUserAccessReport(BaseModel):
    project_id: str
    login_token: Optional[str]
    headers: Optional[Any]
    cookies: Optional[Any]
    tz: Optional[str] = "UTC"


class UserBasicInfo(BaseModel):
    username: str
    email: str
    project_name: Optional[str]
    name: str
    phonenumber: Optional[List] = []


class UserHeader(BaseModel):
    project_id: str
