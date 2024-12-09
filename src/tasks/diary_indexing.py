from asgiref.sync import async_to_sync

from app.celery import celery_app
from app.config import settings
from app.database import get_db, sessionmanager
from app.elastic import es
from dao.diary import NoteDAO

sessionmanager.init(settings.DB_URL)


async def prepare_for_reindexing() -> int | None:
    s = await anext(get_db())
    amount = await NoteDAO(s).count()
    await es.create_index("diary")
    return amount


async def index_notes_batch(offset: int, limit: int = 1000) -> None:
    s = await anext(get_db())
    notes = await NoteDAO(s).all_paginated(offset, limit)

    documents = [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at,
            "diary_id": note.diary_id,
            "user_id": note.diary.user_id,
        }
        for note in notes
    ]

    await es.insert_documents("diary", documents)


@celery_app.task
def reindex_diary() -> None:
    amount = async_to_sync(prepare_for_reindexing)()

    for offset in range(0, amount + 1, 1000):
        reindex_notes_batch.delay(offset)


@celery_app.task
def reindex_notes_batch(offset: int) -> None:
    async_to_sync(index_notes_batch)(offset)
