from datetime import date
from typing import Dict, Any, List, Tuple

import phonenumbers
from phonenumbers import PhoneNumberFormat
from sqlalchemy import select, and_, func
from sqlalchemy.exc import SQLAlchemyError

from database.engine import session_maker
from database.models import Poll, Question, AnswerOption, Answer, User, PollAvailability
from repo.role_repo import attach
from repo.user_repo import find_user_by_phone, insert


async def register(
        user: Dict[str, Any],
        user_id: int,
        chat_id: int
) -> None:
    await insert(user, user_id, chat_id)
    await attach(user_id, user['role'])


async def create_poll(poll: Dict[str, Any], psy_id: int) -> None:
    async with session_maker() as session:
        new_poll = Poll(
            psychologist_id=psy_id,
            title=poll['title'],
            description=poll['description']
        )
        session.add(new_poll)
        await session.flush()

        for question_data in poll['questions']:
            new_question = Question(
                poll_id=new_poll.id,
                text=question_data['name'],
                answer_type=question_data['answer_type']
            )
            session.add(new_question)
            await session.flush()

            if question_data['answer_type'] == 'free':
                continue

            for option_index, option_text in question_data['options'].items():
                new_option = AnswerOption(
                    question_id=new_question.id,
                    value=option_text
                )
                session.add(new_option)

        await session.commit()


async def create_answers(
        answers: List[Dict[str, Any]],
        user_id: int,
        poll_id: int
) -> None:
    async with session_maker() as session:
        for answer in answers:
            new_answer = Answer(
                user_id=user_id,
                poll_id=int(poll_id),
                question_id=int(answer['question_id']),
                text=str(answer['answer']),
            )
            session.add(new_answer)
        await session.commit()


async def collect_history_by_patient(patient_id: int, psy_id: int):
    async with session_maker() as session:
        query = (
            select(
                User.fio,
                User.phone,
                Answer.text.label('answer_text'),
                Question.text.label('question_text'),
                Answer.created.label('answer_date')
            )
            .select_from(User)
            .join(Answer, Answer.user_id == patient_id)
            .join(Question, Answer.question_id == Question.id)
            .join(Poll, Answer.poll_id == Poll.id)
            .filter(
                and_(
                    Poll.psychologist_id == psy_id,
                    User.id == patient_id
                )
            )
            .order_by(User.fio, Answer.created)
        )

        result = await session.execute(query)
        rows = result.fetchall()
        return rows


async def collect_polls_info_by_psy(user_id: int):
    async with session_maker() as session:
        query = (
            select(
                User.fio,
                User.phone,
                Answer.text.label('answer_text'),
                Question.text.label('question_text'),
                Answer.created.label('answer_date')
            )
            .join(Answer, User.id == Answer.user_id)
            .join(Question, Answer.question_id == Question.id)
            .join(Poll, Answer.poll_id == Poll.id)
            .filter(Poll.psychologist_id == user_id)
            .order_by(User.fio, Answer.created)
        )
        result = await session.execute(query)
        rows = result.fetchall()
        return rows


async def give_polls_access_to_user(
        phone: str,
        polls: List[int],
        psy_id: int
) -> None:
    try:
        number = phonenumbers.parse(phone, 'RU')
        if not phonenumbers.is_valid_number(number):
            print("Invalid phone number")

        formatted_number = phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)
        user = await find_user_by_phone(formatted_number)

        new_polls = [
            PollAvailability(
                poll_id=poll_id,
                user_id=user.id,
                psy_id=psy_id
            )
            for poll_id in polls
        ]

        async with session_maker() as session:
            session.add_all(new_polls)
            await session.commit()

    except phonenumbers.NumberParseException:
        print("Failed to parse the phone number")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")


async def get_user_chat_id_with_not_passed_polls() -> List[Tuple[int, str]]:
    today = date.today()
    async with session_maker() as session:
        query = (
            select(
                User.chat_id.label("chat_id"),
                Poll.title.label("title")
            )
            .join(PollAvailability, User.id == PollAvailability.user_id)
            .join(Poll, PollAvailability.poll_id == Poll.id)
            .outerjoin(Answer, and_(
                Answer.user_id == User.id,
                Answer.poll_id == Poll.id,
                func.date(Answer.created) == today
            ))
            .filter(Answer.id.is_(None))
        )

        results = await session.execute(query)

        return [(row[0], row[1]) for row in results.all()]
