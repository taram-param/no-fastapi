from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import sessionmanager
from app.elastic import es
from services.oauth import get_user

load_dotenv()


def init_app(is_test=False):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if is_test:
            sessionmanager.init(settings.TEST_DATABASE_URL)
        else:
            sessionmanager.init(settings.DB_URL)
        yield
        if not is_test:
            await es.es.close()
        await sessionmanager.close()

    app = FastAPI(title="FastAPI server", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from routers import auth, diary, users

    app.include_router(
        users.router, prefix="/api/v1/users", tags=["users"], dependencies=[Depends(get_user)]
    )
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(
        diary.router, prefix="/api/v1/diary", tags=["diary"], dependencies=[Depends(get_user)]
    )
    from kafka_routers.diary import router as kafka_router

    app.include_router(kafka_router)

    return app


app = init_app()
