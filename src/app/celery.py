from celery.app import Celery

from app.config import settings

redis_url = settings.REDIS_URL

celery_app = Celery(
    "celery",
    broker=redis_url,
    backend=redis_url,
    include=[
        "tasks.test",
        "tasks.diary_indexing",
    ],
)

celery_app.conf.update(result_expires=3600)


celery_app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'tasks.test.periodic_task',
        'schedule': 30.0,
        'args': (16, 16),
    },
}
