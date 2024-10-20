import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import ProgrammingError

from app.config import settings
from app.database import sessionmanager
from main import init_app


# Fixture for setting up the event loop for async tests
@pytest.fixture(scope="session")
async def event_loop(event_loop_policy):
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


# Fixture to create and initialize the test database
@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    try:
        # Initialize the session manager with the test database URL
        sessionmanager.init(settings.TEST_DATABASE_URL)
        await sessionmanager.create_test_database()
    except ProgrammingError:
        await sessionmanager.drop_test_database()
        await sessionmanager.create_test_database()

    yield

    # Drop the test database after tests complete
    await sessionmanager.drop_test_database()


# Fixture to set up the FastAPI app with the test environment
@pytest.fixture(scope="session", autouse=True)
async def test_app():
    # Initialize the app with the test flag set to True
    yield init_app(is_test=True)


# Fixture to create tables before each test and drop them afterward
@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    # Create tables for the test
    async with sessionmanager.connect() as connection:
        await sessionmanager.create_all(connection)
    yield
    # Drop tables after the test
    async with sessionmanager.connect() as connection:
        await sessionmanager.drop_all(connection)


# Fixture for the database session
@pytest.fixture(scope="function")
async def session():
    # Provide a session for each test
    async with sessionmanager.session() as session:
        yield session


# Fixture to provide a test client for making API requests
@pytest.fixture(scope="function")
async def client(test_app):
    # Use AsyncClient with the test app for API calls
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac
