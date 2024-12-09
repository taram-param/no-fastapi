from typing import Generic, TypeVar

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseDAO(Generic[ModelType]):
    """Base Data Access Object class.

    Provides DB CRUD operations for specific model.
    """

    model: ModelType
    compound_fields: dict[str, Base | list[Base]] = {}

    def __init__(self, s: AsyncSession = Depends(get_db)):
        self.s = s

    def _set_fields(self, result: Base, data: dict) -> ModelType:
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
    ) -> list[ModelType]:
        result = await self.s.scalars(select(self.model))

        return result.all()

    async def all_paginated(
        self,
        offset: int,
        limit: int,
    ) -> list[ModelType]:
        result = await self.s.scalars(select(self.model).offset(offset).fetch(limit))

        return result.all()

    async def get(self, model_id: int) -> None | ModelType:
        result = await self.s.scalar(select(self.model).where(self.model.id == model_id))

        return result

    async def create(self, data: dict) -> ModelType:
        result = self.model()

        result = self._set_fields(result, data)

        self.s.add(result)
        await self.s.flush()

        return result

    async def update(self, model_id: int, data: dict) -> ModelType:
        result = await self.get(model_id)

        result = self._set_fields(result, data)

        await self.s.flush()
        return result

    async def delete(self, model_id: int) -> None:
        result = await self.get(model_id)

        await self.s.delete(result)
        await self.s.flush()

    async def count(self) -> int | None:
        result = await self.s.scalar(select(func.count(self.model.id)).select_from(self.model))

        return result
