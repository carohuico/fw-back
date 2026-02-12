import base64
import json
from datetime import timedelta
from uuid import uuid4

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from scripts.config import Service
from scripts.errors import AzureActiveDirectoryAuthenticationError
from scripts.logging import logger


def get_kid(token):
    headers = jwt.get_unverified_header(token)
    if not headers:
        raise AzureActiveDirectoryAuthenticationError("missing headers")
    try:
        return headers["kid"]
    except KeyError as e:
        raise AzureActiveDirectoryAuthenticationError("missing kid") from e


def ensure_bytes(key):
    if isinstance(key, str):
        key = key.encode("utf-8")
    return key


def decode_value(val):
    decoded = base64.urlsafe_b64decode(ensure_bytes(val) + b"==")
    return int.from_bytes(decoded, "big")


def rsa_pem_from_jwk(jwk):
    return (
        RSAPublicNumbers(n=decode_value(jwk["n"]), e=decode_value(jwk["e"]))
        .public_key(default_backend())
        .public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    )


def get_jwk(kid, token_kid, token_n_value):
    try:
        jwt_ks = {"keys": [{"kid": token_kid, "e": "AQAB", "n": token_n_value}]}
        for jwk in jwt_ks.get("keys"):
            if jwk.get("kid") == kid:
                return jwk
        raise AzureActiveDirectoryAuthenticationError("kid not recognized")
    except Exception as ae:
        message = "Unable to validate token"
        logger.error(ae)
        raise AzureActiveDirectoryAuthenticationError(message) from ae


def get_public_key(token, token_kid, token_n_value):
    try:
        return rsa_pem_from_jwk(get_jwk(get_kid(token), token_kid, token_n_value))
    except Exception as ae:
        message = f"Unable to validate token: {ae}"
        raise AzureActiveDirectoryAuthenticationError(message) from ae


def set_saml_user_session(name, email, user_role, redis_db):
    """
    To set the session meta in redis and return session key
    """
    payload = {"name": name, "email": email, "user_role": user_role}
    payload_str = f"saml_aad_user_{json.dumps(payload)}"

    session_key = "$" + str(uuid4()).replace("-", "") + "$"
    redis_db.set(session_key, payload_str)
    redis_db.expire(session_key, timedelta(minutes=Service.lockout_time))
    return session_key


def get_saml_user_session(session_key, redis_db, delete_session=True):
    """
    To retrieve the user meta from redis
    """
    payload_str = redis_db.get(session_key)
    if not payload_str:
        raise ValueError
    payload = json.loads(payload_str.replace("saml_aad_user_", "", 1))
    return payload["name"], payload["email"], payload.get("user_role")


def get_user_name(email: str):
    """
    To get the user name from the email
    """
    if "@" in email:
        return email.split("@")[0]
    raise Exception(f"Invalid e-mail ID!: {email}")
