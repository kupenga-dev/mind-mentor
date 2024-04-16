from typing import List

from sqlalchemy import select

from database.engine import session_maker
from database.models import AnswerType


async def get() -> List[AnswerType]:
    answer_type_smt = select(AnswerType)
    async with session_maker() as session:
        answer_types = await session.execute(answer_type_smt)

        return list(answer_types.scalars().all())
