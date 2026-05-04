import asyncio
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from database import Model
from models.helper import get_db
from models.analysis import Analysis


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


async def prepare_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
        await conn.run_sync(Model.metadata.create_all)

    async with TestingSessionLocal() as session:
        pattern = Analysis(
            key="payment_timeout",
            pattern="TimeoutError",
            severity="high",
            message="Payment service timeout",
            category="payment",
            service="payment-service",
            enabled=True,
            priority=100,
        )
        session.add(pattern)
        await session.commit()


@pytest.fixture()
def client():
    asyncio.run(prepare_test_db())

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()