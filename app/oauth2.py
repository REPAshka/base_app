from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# import secrets
# print(secrets.token_hex(32)) # генерация секретного ключа

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
# парсим все секретные данные из файла окружения .env (config.py)


def create_access_token(data: dict):
    """ Создание личного токена доступа пользователя,
     благодаря которому нельзя зайти в аккаутн другого пользователя, монипулируя кодом программы.
     Так же благодаря токену пользователь может продолжать оставаться залогининым на платформе некоторое время """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def verify_access_token(token: str, credentials_exception):
    """ Валидация токена """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """ Берёт токен, валидирует его, достаёт из него айди"""
    credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                          detail="Could not validate credentials",
                                          headers={"WW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user
