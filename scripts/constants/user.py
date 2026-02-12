import os


class Account:
    unplanned_id = "notification_01"
    planned_id = "notification_02"
    email_preferences = "email_preferences"
    user_action_json = {
        "addOptionalFields": {
            "enableAdd": False,
            "modalInfo": {"config": "profile", "modalTitle": "Profile Information"},
        }
    }
    default_notification_data = [
        {
            "heading": "Unplanned events",
            "description": "Receive emails about issues that can cause an outage",
            "notification_id": unplanned_id,
            "value": False,
        },
        {
            "heading": "Planned events",
            "description": "Receive emails about maintenance that is required to "
            "keep the platform operating at optimal status",
            "notification_id": planned_id,
            "value": False,
        },
    ]
    supported_mime_type = ["image/png", "image/jpeg"]

    image_extensions = [".apng", ".avif", ".gif", ".jpg", ".jpeg", ".jfif", ".pjpeg", ".pjp", ".png"]


class UserRoles:
    root_user = "root_user"
    super_user = "kl_super_admin"


class User:
    user_project_keys = [
        "project_id",
        "AccessLevel",
        "userrole",
        "access_group_ids",
        "landing_page",
        "is_app_user",
        "product_access",
        "app_url",
        "location",
        "department",
        "section",
        "access_level_list",
    ]
