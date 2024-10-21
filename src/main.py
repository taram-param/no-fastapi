from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI

from app.config import settings
from app.database import sessionmanager
from services.kafka_service import kafka_service
from services.oauth import get_user

load_dotenv()


def init_app(is_test=False):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if is_test:
            sessionmanager.init(settings.TEST_DATABASE_URL)
        else:
            sessionmanager.init(settings.DB_URL)
            await kafka_service.start_consumer("spiderweb")
        yield
        if not is_test:
            await kafka_service.close_all_consumers()
        await sessionmanager.close()

    app = FastAPI(title="FastAPI server", lifespan=lifespan)

    from routers import auth, users

    app.include_router(
        users.router, prefix="/api/v1/users", tags=["users"], dependencies=[Depends(get_user)]
    )
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

    return app


app = init_app()
