from jose import jwt
from datetime import datetime, timedelta, timezone
from utils.setting import get_auth_data


def create_token(data: dict):
     to_encode = data.copy()
     expire = datetime.now(timezone.utc) + timedelta(days=30)
     to_encode.update({"exp": expire})
     auth_data = get_auth_data()
     encode_jwt = jwt.encode(to_encode, auth_data["secret_key"], algorithm=auth_data["algorithm"])
     return encode_jwt


def decode_jwt(token: str):
     auth_data = get_auth_data()
     decode_jwt = jwt.decode(token, auth_data["secret_key"], algorithms=[auth_data["algorithm"]])
     return decode_jwt
