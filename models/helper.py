from sqlalchemy.ext.asyncio import (create_async_engine, async_sessionmaker)
from utils.setting import get_db_url
from database import Model
from models.user import User
from models.incident import Incident, IncidentHistory
from models.comment import Comment
from models.analysis import Analysis
from models.event import Event

class Databasehelper:
    def __init__ (self, url:str):
        self.engine = create_async_engine(
            url=url
        )

        self.new_session = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit = False,
            expire_on_commit = False
        )

    async def get_db(self):
        async with self.new_session() as session:
            yield session

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Model.metadata.create_all)

db = Databasehelper(get_db_url())
async def get_db():
    async for session in db.get_db():
        yield session

async def create_tables():
    await db.create_tables()