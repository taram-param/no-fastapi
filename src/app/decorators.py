from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db


class TransactionAtomic:
    def __init__(self, s: AsyncSession = Depends(get_db)):
        self.s = s

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.s.rollback()
            return False

        await self.s.commit()
        return True
