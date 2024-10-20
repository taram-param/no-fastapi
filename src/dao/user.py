from sqlalchemy import select

from dao.base import BaseDAO
from models.user import Address, User
from utils.crypto_utils import hash_password


class UserDAO(BaseDAO):
    model: User = User
    compound_fields = {
        "addresses": [Address],
    }

    async def create(self, data: dict):
        user = self.model()
        if data.get("password"):
            data["password"] = hash_password(data["password"])
        user = self._set_fields(user, data)

        self.s.add(user)
        await self.s.flush()

        return user

    async def get_by_email(self, email):
        address = await self.s.scalar(
            select(Address).join(Address.user).where(Address.email_address == email)
        )
        user = address.user if address else None
        return user
