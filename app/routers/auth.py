from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. database import get_db # одна точка - импорт из текущей папки, две точки - импорт из папки уровня выше
from .. import schemas, models, utils, oauth2

router = APIRouter(tags=["Authentication"])

@router.post('/login', response_model=schemas.Token) # можно логиниться и по мейлу и по логину
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # c OAuth2PasswordRequestForm для проверки в postman используем Body -> form-data, вместо Body -> raw -> JSON
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    # create and return a token
    access_token = oauth2.create_access_token(data={"user_id": user.id}) # передача в токен айди юзера;
    # никогда не передавать в токен много информации или пароль пользователя, т.к. его можно легко декодировать
    return {"access_token": access_token, "token_type": "bearer"}