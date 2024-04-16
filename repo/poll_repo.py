from datetime import date
from typing import List

from sqlalchemy import select, func, and_, not_, exists
from sqlalchemy.orm import selectinload

from database.engine import session_maker
from database.models import Poll, Question, PollAvailability, Answer


async def get_user_polls(user_id: int) -> List[Poll]:
    async with session_maker() as session:
        today = date.today()
        subquery = (
            select(1)
            .select_from(Answer)
            .where(
                and_(
                    Answer.user_id == user_id,
                    func.date(Answer.created) == today,
                    Answer.poll_id == Poll.id
                )
            )
        )

        polls_query = select(Poll).join(
            PollAvailability, PollAvailability.poll_id == Poll.id
        ).filter(
            PollAvailability.user_id == user_id,
            not_(exists(subquery))
        ).distinct()

        result = await session.execute(polls_query)
        polls = result.scalars().all()
        return polls


async def get() -> List[Poll]:
    async with session_maker() as session:
        polls = await session.execute(
            select(Poll)
        )

    return polls.scalars().all()


async def get_poll_with_questions(poll_id: int) -> List[Question]:
    async with session_maker() as session:
        questions = await session.execute(
            select(Question)
            .where(Question.poll_id == poll_id)
            .options(selectinload(Question.answer_options))
        )

    return questions.scalars().all()


async def get_owner_user_polls(psy_id: int) -> List[Poll]:
    async with session_maker() as session:
        polls = await session.execute(
            select(Poll)
            .filter(Poll.psychologist_id == psy_id)
            .distinct()
        )

    return polls.scalars().all()
