import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

# Import models so they register with Base.metadata
import app.models.trip  # noqa: F401
import app.models.video_media  # noqa: F401
from app.api.deps import get_current_user_id, get_db
from app.db.base import Base
from app.main import app as fastapi_app

TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
OTHER_USER_ID = "22222222-2222-2222-2222-222222222222"

# --- SQLite compatibility: compile PG types to SQLite equivalents ---


@compiles(PG_UUID, "sqlite")
def compile_pg_uuid_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


# Use aiosqlite for isolated in-memory test database
_test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    echo=False,
    connect_args={"check_same_thread": False},
)
_test_session_factory = async_sessionmaker(_test_engine, expire_on_commit=False)


@event.listens_for(_test_engine.sync_engine, "connect")
def _register_sqlite_functions(dbapi_conn, connection_record):
    """Register PostgreSQL-compatible functions for SQLite."""
    dbapi_conn.create_function("char_length", 1, len)


@dataclass
class TripFixture:
    """Lightweight test fixture — not an ORM model."""

    id: uuid.UUID
    owner_id: uuid.UUID
    title: str


@pytest.fixture(autouse=True)
async def _setup_db():
    """Create test tables before each test and drop after."""
    target_tables = [
        Base.metadata.tables["trips"],
        Base.metadata.tables["video_media"],
    ]
    async with _test_engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys = ON"))
        for table in target_tables:
            await conn.run_sync(lambda sync_conn, t=table: t.create(sync_conn, checkfirst=True))
    yield
    async with _test_engine.begin() as conn:
        for table in reversed(target_tables):
            await conn.run_sync(lambda sync_conn, t=table: t.drop(sync_conn, checkfirst=True))


async def _override_get_db() -> AsyncIterator[AsyncSession]:
    async with _test_session_factory() as session:
        await session.execute(text("PRAGMA foreign_keys = ON"))
        yield session


# Apply dependency overrides
fastapi_app.dependency_overrides[get_db] = _override_get_db
fastapi_app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def test_trip() -> TripFixture:
    """Create a trip owned by TEST_USER_ID for use in tests."""
    from app.models.trip import Trip

    trip_id = uuid.uuid4()
    async with _test_session_factory() as session:
        trip = Trip(
            id=trip_id,
            owner_id=uuid.UUID(TEST_USER_ID),
            title="Test Trip",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
        )
        session.add(trip)
        await session.commit()
    return TripFixture(id=trip_id, owner_id=uuid.UUID(TEST_USER_ID), title="Test Trip")


@pytest.fixture
async def other_user_trip() -> TripFixture:
    """Create a trip owned by OTHER_USER_ID (not the authenticated test user)."""
    from app.models.trip import Trip

    trip_id = uuid.uuid4()
    async with _test_session_factory() as session:
        trip = Trip(
            id=trip_id,
            owner_id=uuid.UUID(OTHER_USER_ID),
            title="Other User Trip",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
        )
        session.add(trip)
        await session.commit()
    return TripFixture(
        id=trip_id, owner_id=uuid.UUID(OTHER_USER_ID), title="Other User Trip"
    )
