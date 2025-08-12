from sqlalchemy import Sequence, select

from dao.base import BaseDAO
from models.diary import Diary, Note


class DiaryDAO(BaseDAO[Diary]):
    model: type[Diary] = Diary
    compound_fields = {
        "notes": [Note], # type: ignore
    }

    async def get_by_user(self, user_id: int) -> Diary | None:
        diary = await self.s.scalar(select(Diary).join(Diary.user).where(Diary.user_id == user_id))

        return diary


class NoteDAO(BaseDAO[Note]):
    model: type[Note] = Note

    async def get_by_diary(self, diary_id: int) -> Sequence[Note]:
        notes = await self.s.scalars(select(Note).join(Note.diary).where(Note.diary_id == diary_id))

        return notes.all()

    async def get_by_user(self, user_id: int) -> Sequence[Note]:
        notes = await self.s.scalars(
            select(Note).join(Note.diary).where(Diary.user_id == user_id)
        )

        return notes.all()
