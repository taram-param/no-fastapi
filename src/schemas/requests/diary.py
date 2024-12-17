from app.schemas import ExtendedBaseModel


class CreateDiarySchema(ExtendedBaseModel):
    user_id: int


class CreateNoteSchema(ExtendedBaseModel):
    title: str
    content: str
    diary_id: int
