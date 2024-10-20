from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from dao.user import UserDAO
from schemas.requests import auth
from services.clients.google_client import GoogleClient
from services.oauth import create_token
from utils.crypto_utils import verify_password

router = APIRouter()


@router.post("/register")
async def register(payload: auth.RegisterUserSchema, s: AsyncSession = Depends(get_db)):
    data = {"addresses": [{"email_address": payload.email}], "password": payload.password}
    user = await UserDAO(s).create(data=data)

    await s.commit()
    await s.refresh(user)
    return user


@router.post("/verify")
async def verify_email(payload: int):
    # TODO: implement verify
    pass


@router.post("/forgot")
async def forgot_email(payload: int):
    # TODO: forgot
    pass


@router.post("/login")
async def login(
    payload: auth.LoginUserSchema,
    s: AsyncSession = Depends(get_db),
):
    user = await UserDAO(s).get_by_email(payload.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong Email or Password",
        )

    if not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong Email or Password",
        )

    access_token = create_token(
        data={"type": "access", "user_id": user.id},
        expires_delta=timedelta(minutes=60 * 24),
    )
    refresh_token = create_token(
        data={"type": "refresh", "user_id": user.id},
        expires_delta=timedelta(minutes=60 * 24 * 7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.get("/login/google")
async def login_google():
    url = GoogleClient().get_google_oauth_url()
    return {"url": url}


@router.get("/auth/google")
async def auth_google(
    code: str, s: AsyncSession = Depends(get_db), user_dao: UserDAO = Depends(UserDAO)
):
    user_info = await GoogleClient().get_user_info(code)
    email = user_info.get("email")
    user = await user_dao.get_by_email(email)

    if not user:
        user = await user_dao.create({"addresses": [{"email_address": email}]})

    access_token = create_token(
        data={"type": "access", "user_id": user.id},
        expires_delta=timedelta(minutes=60 * 24),
    )
    refresh_token = create_token(
        data={"type": "refresh", "user_id": user.id},
        expires_delta=timedelta(minutes=60 * 24 * 7),
    )

    await s.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
