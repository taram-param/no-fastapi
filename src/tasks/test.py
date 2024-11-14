from app.celery import celery_app


@celery_app.task
def test():
    print("hello")


@celery_app.task
def periodic_task(a, b):
    return a + b
