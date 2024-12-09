from datetime import datetime

from app.schemas import ExtendedBaseModel


class DiarySchema(ExtendedBaseModel):
    id: int
    user_id: int


class NoteSchema(ExtendedBaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    diary_id: int
