from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from joserfc import jwt
from joserfc.errors import JoseError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from dao.user import UserDAO
from models.user import User

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
# TODO: Profile the auth process and add cache if possible
security = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/swagger_login")


def refresh_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = token.claims
        token_type = token_data.get("type")
        user_id = token_data.get("user_id")
        is_active = token_data.get("active")
        expiration_time = token_data.get("exp")

        if token_type != "refresh":
            raise credentials_exception

        if user_id is None:
            raise credentials_exception

        if datetime.now(timezone.utc) > datetime.fromtimestamp(expiration_time, tz=timezone.utc):
            raise credentials_exception

        if not is_active:
            raise credentials_exception

    except ValueError:
        raise credentials_exception

    access_token = create_token(
        {"type": "access", "user_id": user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MIN),
    )

    return access_token


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        header={"alg": ALGORITHM},
        claims=to_encode,
        key=SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    return encoded_jwt


async def get_user(token: str = Depends(security), s: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = token.claims
        token_type = token_data.get("type")
        user_id = token_data.get("user_id")
        expiration_time = token_data.get("exp")

        if token_type != "access":
            raise credentials_exception

        if user_id is None:
            raise credentials_exception

        if datetime.now(timezone.utc) > datetime.fromtimestamp(expiration_time, tz=timezone.utc):
            raise credentials_exception

    except JoseError:
        raise credentials_exception

    user = await UserDAO(s).get(user_id)

    if user is None:
        raise credentials_exception

    return user


class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[User, Depends(get_user)]):
        if user.role == "superuser" or user.role in self.allowed_roles:
            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have enough permissions",
        )
