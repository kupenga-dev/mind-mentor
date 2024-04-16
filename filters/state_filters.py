import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat
from sqlalchemy import select, func

from database.engine import session_maker
from database.models import AnswerType
from repo.user_repo import find_user_by_phone


async def is_yes_no_answers(message: str) -> bool:
    return message == 'да' or message == 'нет'


async def is_correct_answer_type(message: str) -> bool:
    if not message:
        return False

    async with session_maker() as session:
        query = select([func.count()]).where(AnswerType.name == message)
        result = await session.scalar(query)

    return result > 0


async def is_correct_phone_number(message: str) -> bool:
    try:
        number = phonenumbers.parse(message, 'RU')

        if not phonenumbers.is_possible_number(number):
            return False

        if not phonenumbers.is_valid_number(number):
            return False

    except NumberParseException:
        return False

    return True


async def has_user_with_this_phone_number(message: str) -> bool:
    number = phonenumbers.parse(message, 'RU')
    formatted_number = phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)

    user = await find_user_by_phone(formatted_number)

    if user is None:
        return False

    return True
