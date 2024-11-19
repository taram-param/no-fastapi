import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import ProgrammingError

from app.config import settings
from app.database import sessionmanager
from app.redis import redis_client
from main import init_app
from services.oauth import get_user


@pytest.fixture(scope="session")
async def event_loop(event_loop_policy):
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    try:
        sessionmanager.init(settings.TEST_DATABASE_URL)
        await sessionmanager.create_test_database()
    except ProgrammingError:
        await sessionmanager.drop_test_database()
        await sessionmanager.create_test_database()

    yield

    await sessionmanager.drop_test_database()


@pytest.fixture(scope="session", autouse=True)
async def test_app():
    yield init_app(is_test=True)


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with sessionmanager.connect() as connection:
        await sessionmanager.create_all(connection)
    yield
    async with sessionmanager.connect() as connection:
        await sessionmanager.drop_all(connection)


@pytest.fixture(scope="function", autouse=True)
async def invalidate_redis():
    await redis_client.flushdb()


@pytest.fixture(scope="function")
async def session():
    async with sessionmanager.session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def skip_auth(test_app):
    def _skip_auth():
        pass

    test_app.dependency_overrides[get_user] = _skip_auth
