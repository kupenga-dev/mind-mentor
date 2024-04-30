from aiogram.types import ReplyKeyboardMarkup, BotCommand

from enums.enums import RoleSlugEnum
from keyboards.reply import KeyboardBuilder
from repo.user_repo import UserRepo

private = [
    BotCommand(command='back', description='Назад'),
    BotCommand(command='cancel', description='Отменить'),
]


USER_KB = KeyboardBuilder.get_keyboard(
    "Об опросах",
    "Мои опросы",
    placeholder="Выберите действие",
    sizes=(2,)
)

PSYCHOLOGIST_KB = KeyboardBuilder.get_keyboard(
    "Создать опрос",
    "Получить историю по клиенту",
    "Получить историю опросов",
    "Дать доступ к опросу",
    placeholder="Выберите действие",
    sizes=(2,)
)

SYSTEM_KB = KeyboardBuilder.get_keyboard(
    "О нас",
    "Регистрация",
    placeholder="Выберите действие",
    sizes=(2,)
)


async def get_role_keyboard(role_slug: str) -> ReplyKeyboardMarkup:
    if role_slug == RoleSlugEnum.USER.value:
        return USER_KB
    if role_slug == RoleSlugEnum.PSYCHOLOGIST.value:
        return PSYCHOLOGIST_KB

    return SYSTEM_KB


async def get_keyboard_by_id(user_id: int) -> ReplyKeyboardMarkup:
    user_repo = UserRepo()
    user_role = await user_repo.get_user_role(user_id)

    return await get_role_keyboard(user_role)
