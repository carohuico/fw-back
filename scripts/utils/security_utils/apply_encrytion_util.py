import uuid
from datetime import datetime, timedelta

from jose import jwt
from scripts.constants import Secrets, JWTSecrets


def create_token(user_id, email_id, role, ip, token, role_id, age=Secrets.LOCK_OUT_TIME_MINS):
    """
    This method is to create a cookie
    """
    try:
        uid = str(uuid.uuid4()).replace("-", "")

        payload = {
            "ip": ip,
            "user_id": user_id,
            "email_id": email_id,
            "token": token,
            "uid": uid,
            "role": role,
            "role_id": role_id
        }

        exp = datetime.utcnow() + timedelta(minutes=age)
        _extras = {"iss": Secrets.issuer, "exp": exp}
        _payload = {**payload, **_extras}

        new_token = jwt.encode(_payload)

        print("Updated Session")
        return uid
    except Exception:
        raise


def create_access_token(subject: dict, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=JWTSecrets.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": subject.get("user_id"),
        "email": subject.get("email"),
        "user_type": subject.get("user_type")
    }
    to_encode = {"exp": expires_delta, **payload}
    encoded_jwt = jwt.encode(to_encode, JWTSecrets.JWT_SECRET_KEY, JWTSecrets.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: dict, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=JWTSecrets.REFRESH_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": subject.get("user_id"),
        "email": subject.get("email"),
        "user_type": subject.get("user_type")
    }
    to_encode = {"exp": expires_delta, **payload}
    encoded_jwt = jwt.encode(to_encode, JWTSecrets.JWT_REFRESH_SECRET_KEY, JWTSecrets.ALGORITHM)
    return encoded_jwt
