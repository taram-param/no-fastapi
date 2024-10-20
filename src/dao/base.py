from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Base


class BaseDAO:
    """Base Data Access Object class.

    Provides DB CRUD operations for specific model.
    """

    model: Base
    compound_fields: dict[str, Base | list[Base]]

    def __init__(self, s: AsyncSession = Depends(get_db)):
        self.s = s

    def _set_fields(self, result: Base, data: dict) -> Base:
        for field in data:
            if field in self.compound_fields:
                if isinstance(self.compound_fields[field], list):
                    setattr(
                        result,
                        field,
                        [
                            self.compound_fields[field][0](**field_element)
                            for field_element in data[field]
                        ],
                    )
                else:
                    setattr(
                        result,
                        field,
                        self.compound_fields[field](**data[field]),
                    )
            else:
                setattr(result, field, data[field])

        return result

    async def all(
        self,
    ):
        result = await self.s.scalars(select(self.model))

        return result.all()

    async def get(self, model_id: int):
        result = await self.s.get(self.model, model_id)
        if result is None:
            raise HTTPException(404, "User not found")

        return result

    async def create(self, data: dict):
        result = self.model()

        result = self._set_fields(result, data)

        self.s.add(result)
        await self.s.flush()

        return result

    async def update(self, model_id: int, data: dict):
        result = await self.get(model_id)

        result = self._set_fields(result, data)

        await self.s.flush()
        return result

    async def delete(self, model_id: int):
        result = await self.get(model_id)

        await self.s.delete(result)
        await self.s.flush()
