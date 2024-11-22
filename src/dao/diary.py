from sqlalchemy import select

from dao.base import BaseDAO
from models.diary import Diary, Note


class DiaryDAO(BaseDAO):
    model: Diary = Diary
    compound_fields = {
        "notes": [Diary],
    }

    async def get_by_user(self, user_id) -> Diary | None:
        diary = await self.s.scalar(select(Diary).join(Diary.user).where(Diary.user_id == user_id))

        return diary


class NoteDAO(BaseDAO):
    model: Note = Note

    async def get_by_diary(self, diary_id) -> Note | None:
        notes = await self.s.scalars(select(Note).join(Note.diary).where(Note.diary_id == diary_id))

        return notes.all()
