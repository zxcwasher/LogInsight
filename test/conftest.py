import asyncio
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from database import Model
from models.helper import get_db

from models.user import User
from models.incident import Incident, IncidentHistory
from models.comment import Comment
from models.analysis import Analysis
from models.event import Event
import os

os.environ["SKIP_DB_STARTUP"] = "1"

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
        await conn.run_sync(Model.metadata.create_all)


@pytest.fixture
def client():
    asyncio.run(reset_db())

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()