from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import token, database, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_user(email):
    db = next(database.get_db())
    return db.query(models.User).filter(models.User.email == email).first()


def get_current_user(data: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = token.verify_token(data, credentials_exception)
    user = get_user(token_data.email)
    return user

