from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from dao.user import UserDAO
from schemas.requests import user as user_request
from schemas.responses import user as user_response

router = APIRouter()


@router.get("/", response_model=list[user_response.UserSchema])
async def get_users(
    s: AsyncSession = Depends(get_db),
    user_dao: UserDAO = Depends(UserDAO),
):
    users = await user_dao.all()

    return users


@router.get("/{user_id}", response_model=user_response.UserSchema)
async def get_user(
    user_id: int,
    s: AsyncSession = Depends(get_db),
    user_dao: UserDAO = Depends(UserDAO),
):
    user = await user_dao.get(user_id)

    return user


@router.post("/", response_model=user_response.UserSchema)
async def create_user(
    payload: user_request.CreateUserSchema,
    s: AsyncSession = Depends(get_db),
    user_dao: UserDAO = Depends(UserDAO),
):
    data = payload.model_dump()
    user = await user_dao.create(data)

    await s.commit()
    await s.refresh(user)
    return user


@router.put("/{user_id}", response_model=user_response.UserSchema)
async def update_user(
    user_id: int,
    payload: user_request.UpdateUserSchema,
    s: AsyncSession = Depends(get_db),
    user_dao: UserDAO = Depends(UserDAO),
):
    data = payload.model_dump(exclude_unset=True)
    user = await user_dao.update(user_id, data)

    await s.commit()
    await s.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    s: AsyncSession = Depends(get_db),
    user_dao: UserDAO = Depends(UserDAO),
):
    await user_dao.delete(user_id)

    await s.commit()
    return {"status": "ok"}
