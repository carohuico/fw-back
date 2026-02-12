from datetime import datetime
from typing import Union, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from scripts.constants import JWTSecrets
from scripts.constants.app_constants import TableName
from scripts.constants.app_routes import EndPoints
from scripts.utils.sql_db_utils import DBUtility

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl=EndPoints.app_base_url+EndPoints.api_login,
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(reuseable_oauth)):
    try:
        payload = jwt.decode(
            token, JWTSecrets.JWT_SECRET_KEY, algorithms=[JWTSecrets.ALGORITHM]
        )
        token_data = payload

        if datetime.fromtimestamp(token_data.get('exp')) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_conn = DBUtility()
    user_data = f'''select * 
                    from {TableName.table_user_details}
                    where user_id = '{token_data.get('user_id')}' '''
    user_status_flag, query_resp = db_conn.select_mysql_fetchone(user_data)
    user: Union[dict[str, Any], None] = query_resp if user_status_flag else None

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user