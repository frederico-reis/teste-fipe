import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = "fipe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  #Tempo de expiração do token em minutos

def generate_token(user_id, password):

    expiration_date = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"user_id":user_id, "password":password, "exp":expiration_date}
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm="HS256")

    return encoded_jwt

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token Inválido")