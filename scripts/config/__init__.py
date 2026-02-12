import os
import sys
from configparser import SafeConfigParser, BasicInterpolation
from pydantic import BaseSettings


class EnvInterpolation(BasicInterpolation):
    """
    Interpolation which expands environment variables in values.
    """

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)

        if not os.path.expandvars(value).startswith('$'):
            return os.path.expandvars(value)
        else:
            return


try:
    config = SafeConfigParser(interpolation=EnvInterpolation())
    config.read(f"conf/application.conf")
except Exception as e:
    print(f"Error while loading the config: {e}")
    print("Failed to Load Configuration. Exiting!!!")
    sys.exit()


class Configuration(BaseSettings):
    port: int = config["SERVICE"]["port"]
    host: str = config["SERVICE"]["host"]
    cookie_max_age: int = config.getint("SERVICE", "cookie_max_age_in_mins", fallback=60)
    secure_cookie: bool = config["SERVICE"]["secure_cookie_flag"]

    LOCK_OUT_TIME_MINS: int = config["LOGIN_EXPIRY"]["lockout_time_minutes"]

    password_decryption_key = config.get("PASSWORD_KEY", "password_decryption_key")

    MODULE_PROXY: str = config['PROXY']['module_proxy']

    AAD_CLIENT_ID: str = config["AZURE_AD_AUTH"]["AAD_CLIENT_ID"]
    AAD_TENANT_ID: str = config["AZURE_AD_AUTH"]["AAD_TENANT_ID"]
    API_SCOPE: str = config["AZURE_AD_AUTH"]["API_SCOPE"]
    ISSUER_AUTHORITY: str = config["AZURE_AD_AUTH"]["ISSUER_AUTHORITY"]

    AAD_ADD_NEW_USERS: str = config["AZURE_AD_AUTH"]["AAD_ADD_NEW_USERS"]
    AAD_USER_DEFAULT_PROJECT_ID: str = config["AZURE_AD_AUTH"]["AAD_USER_DEFAULT_PROJECT_ID"]
    AAD_USER_DEFAULT_ACCESS_GROUP_ID: str = config["AZURE_AD_AUTH"]["AAD_USER_DEFAULT_ACCESS_GROUP_ID"]
    AAD_USER_DEFAULT_ROLE_ID: str = config["AZURE_AD_AUTH"]["AAD_USER_DEFAULT_ROLE_ID"]

    AS_REDIRECT_URL: str = config["AZURE_SAML_AUTH"]["AS_REDIRECT_URL"]

    SAML_NAME_ATTRIBUTE_VALUE: str = config.get("SAML", "name_attribute_value")
    SAML_EMAIL_ATTRIBUTE_VALUE: str = config.get("SAML", "email_attribute_value")

    SQL_HOST: str = config["SQL"]["HOST"]
    SQL_PORT: int = config["SQL"]["PORT"]
    SQL_USER_NAME: str = config["SQL"]["USER_NAME"]
    SQL_PASSWORD: str = config["SQL"]["PASSWORD"]
    SQL_DB_NAME: str = config["SQL"]["DB_NAME"]

    base_path: str = config["DIRECTORIES"]["base_path"]

    plm_base_url: str = config["PLM"]["plm_base_url"]
    plm_hcm_base_url: str = config["PLM"]["plm_hcm_base_url"]
    plm_allowed_classes: list = list(config["PLM"]["plm_allowed_classes"].split(','))
    plm_org: str = config["PLM"]["plm_org"]
    plm_bom: str = config["PLM"]["plm_bom"]
    plm_token: str = config["PLM"]["plm_token"]


_conf = Configuration()


class Service:
    port = _conf.port
    host = _conf.host
    cookie_max_age = _conf.cookie_max_age
    MODULE_PROXY = _conf.MODULE_PROXY
    lockout_time = _conf.LOCK_OUT_TIME_MINS

    secure_cookie = _conf.secure_cookie
    cookie_timeout = int(os.environ.get("COOKIE_TIMEOUT", default="1440")) * 60

    add_session_id: bool = os.environ.get("ADD_SESSION_ID", default=True) in [
        "True",
        "true",
        True,
    ]



class AzureADConf:
    AAD_CLIENT_ID = _conf.AAD_CLIENT_ID
    AAD_TENANT_ID = _conf.AAD_TENANT_ID
    API_SCOPE = _conf.API_SCOPE
    ISSUER_AUTHORITY = _conf.ISSUER_AUTHORITY

    AAD_ADD_NEW_USERS = _conf.AAD_ADD_NEW_USERS
    AAD_USER_DEFAULT_PROJECT_ID = _conf.AAD_USER_DEFAULT_PROJECT_ID
    AAD_USER_DEFAULT_ACCESS_GROUP_ID = _conf.AAD_USER_DEFAULT_ACCESS_GROUP_ID
    AAD_USER_DEFAULT_ROLE_ID = _conf.AAD_USER_DEFAULT_ROLE_ID

    OAUTH_CONFIG_OUTPUT = {
        "clientId": AAD_CLIENT_ID,
        "scope": API_SCOPE,
        "issuer": ISSUER_AUTHORITY,
    }

    AS_REDIRECT_URL = _conf.AS_REDIRECT_URL
    password_decryption_key = _conf.password_decryption_key


class SQLDBConf:
    SQL_HOST = _conf.SQL_HOST
    SQL_PORT = _conf.SQL_PORT
    SQL_USER_NAME = _conf.SQL_USER_NAME
    SQL_PASSWORD = _conf.SQL_PASSWORD
    SQL_DB_NAME = _conf.SQL_DB_NAME


class KeyPath(object):
    public = os.path.join("data", "keys", "public")
    private = os.path.join("data", "keys", "private")


class SAML:
    NAME_KEY_VALUE = _conf.SAML_NAME_ATTRIBUTE_VALUE
    EMAIL_KEY_VALUE = _conf.SAML_EMAIL_ATTRIBUTE_VALUE


class PathsToDirectories:
    BASE_MOUNT = _conf.base_path
    IMAGE_PATH = os.path.join(BASE_MOUNT, "images")


class PLMConf:
    plm_base_url = _conf.plm_base_url
    plm_hcm_base_url = _conf.plm_hcm_base_url
    plm_allowed_classes = _conf.plm_allowed_classes
    plm_bom = _conf.plm_bom
    plm_org = _conf.plm_org
    plm_token = _conf.plm_token
