import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import MetaData

from database import fixtures
from database.models import BaseModel

engine = create_async_engine(os.getenv('DB_URL'), echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
metadata = MetaData()


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def drop_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


async def add_roles() -> None:
    async with session_maker() as session:
        await fixtures.add_roles(session)
        await fixtures.add_answer_types(session)
        await fixtures.add_polls(session)
        await fixtures.add_questions(session)
        # await session.commit()


async def check_and_fill_db() -> None:

    roles_table = metadata.tables.get('roles')

    if roles_table is None:
        await create_tables()
        await add_roles()
