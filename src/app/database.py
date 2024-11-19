import contextlib
from typing import AsyncIterator

import asyncpg
from sqlalchemy import make_url, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.models import Base


class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, url: str):
        self._engine = create_async_engine(url, echo=False, pool_size=50, max_overflow=10)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Used for testing
    async def create_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.drop_all)

    async def create_test_database(self):
        # Parse the URL to get the database name
        url = make_url(settings.TEST_DATABASE_URL)
        database_name = url.database

        # Temporarily connect to the 'postgres' default database to create the new test database
        url = url.set(database="postgres")
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

        async with engine.connect() as connection:
            try:
                await connection.execute(text(f"CREATE DATABASE {database_name}"))
                print(f"Database {database_name} created successfully.")
            except asyncpg.DuplicateDatabaseError:
                print(f"Database {database_name} already exists, continuing...")
                raise
            except Exception as e:
                print(f"An error occurred while creating the database: {e}")
                raise
            finally:
                await engine.dispose()

    async def drop_test_database(self):
        # Parse the URL to get the database name
        url = make_url(settings.TEST_DATABASE_URL)
        database_name = url.database

        # Temporarily connect to the 'postgres' default database to drop the test database
        url = url.set(database="postgres")
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

        async with engine.connect() as connection:
            try:
                # Terminate any connections to the test database before dropping it
                await connection.execute(
                    text(
                        f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                        f"FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database_name}' "
                        f"AND pid <> pg_backend_pid();"
                    )
                )
                # Drop the database
                await connection.execute(text(f"DROP DATABASE IF EXISTS {database_name}"))
                print(f"Database {database_name} dropped successfully.")
            except ProgrammingError as e:
                print(f"Error dropping database {database_name}: {e}")
            finally:
                await engine.dispose()


sessionmanager = DatabaseSessionManager()


async def get_db():
    async with sessionmanager.session() as session:
        yield session
