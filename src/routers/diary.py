from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.elastic import es
from dao.diary import DiaryDAO, NoteDAO
from schemas.requests.diary import CreateNoteSchema
from schemas.responses.diary import DiarySchema, NoteSchema
from schemas.responses.user import UserSchema
from services.elastic_documents.notes import Note
from services.oauth import get_user

router = APIRouter()


@router.get("/", response_model=list[DiarySchema])
async def get_diaries(
    user: UserSchema = Depends(get_user),
    s: AsyncSession = Depends(get_db),
    diary_dao: DiaryDAO = Depends(DiaryDAO),
):
    diary = await diary_dao.get_by_user(user.id)
    await s.commit()
    await s.refresh(diary)
    return diary


@router.get("/{diary_id}", response_model=DiarySchema)
async def get_diary(
    diary_id: int,
    user: UserSchema = Depends(get_user),
    s: AsyncSession = Depends(get_db),
    diary_dao: DiaryDAO = Depends(DiaryDAO),
):
    diary = await diary_dao.get(diary_id)

    return diary


@router.post("/", response_model=DiarySchema)
async def create_diary(
    user: UserSchema = Depends(get_user),
    s: AsyncSession = Depends(get_db),
    diary_dao: DiaryDAO = Depends(DiaryDAO),
):
    diary = await diary_dao.create({"user_id": user.id})
    await s.commit()
    await s.refresh(diary)

    return diary


@router.get("/{diary_id}/notes/", response_model=list[NoteSchema])
async def get_notes_by_diary(
    diary_id: int,
    q: str | None = None,
    s: AsyncSession = Depends(get_db),
    note_dao: NoteDAO = Depends(NoteDAO),
):
    if q:
        result = await es.search(
            "diary",
            q,
            ["title", "content"],
            {"diary_id": diary_id},
        )
    else:
        result = await note_dao.get_by_diary(diary_id)

    return result


@router.get("/notes/", response_model=list[NoteSchema])
async def get_notes_by_user(
    q: str | None = None,
    user: UserSchema = Depends(get_user),
    s: AsyncSession = Depends(get_db),
    note_dao: NoteDAO = Depends(NoteDAO),
):
    if q:
        result = await es.search(
            "diary",
            q,
            ["title", "content"],
            {"user_id": user.id},
        )
    else:
        result = await note_dao.get_by_user(user.id)

    return result


@router.get("/notes/{note_id}/", response_model=NoteSchema)
async def get_note(
    note_id: int,
    user: UserSchema = Depends(get_user),
    s: AsyncSession = Depends(get_db),
    note_dao: NoteDAO = Depends(NoteDAO),
):
    result = await note_dao.get(note_id)

    return result


@router.post("/notes/", response_model=NoteSchema)
async def create_note(
    payload: CreateNoteSchema,
    user: UserSchema = Depends(get_user),
    s: AsyncSession = Depends(get_db),
    note_dao: NoteDAO = Depends(NoteDAO),
):
    data = payload.model_dump()
    note = await note_dao.create(data)
    await s.commit()
    await s.refresh(note)
    await Note(
        meta={"id": note.id},
        id=note.id,
        title=note.title,
        content=note.content,
        created_at=note.created_at,
        diary_id=note.diary_id,
        user_id=user.id,
    ).save()
    return note
