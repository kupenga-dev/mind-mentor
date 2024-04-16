import asyncio
from typing import List, Callable, Coroutine, Any, TypeVar, Union

from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Poll, User
from repo.poll_repo import get_user_polls, get, get_owner_user_polls


T = TypeVar('T')


async def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


async def collect_poll_list() -> ReplyKeyboardMarkup:
    polls = await get()

    return await make_poll_inline_list(polls)


async def collect_user_poll_list(user_id: int) -> ReplyKeyboardMarkup | None:
    polls = await get_user_polls(user_id)
    print(polls)
    if not polls:
        return None

    return await make_poll_inline_list(polls)


async def create_inline_keyboard(
        items: List[T],
        button_formatter: Callable[
            [T],
            Union[
                InlineKeyboardButton,
                Coroutine[Any, Any, InlineKeyboardButton]
            ]
        ],
        buttons_per_row: int = 3,
        sizes: tuple[int] = (3,)
) -> ReplyKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for i, item in enumerate(items, start=1):
        # If button_formatter is truly async, it should be awaited
        button = await button_formatter(item) \
            if asyncio.iscoroutinefunction(button_formatter) \
            else await button_formatter(item)
        keyboard.add(button)

        if i % buttons_per_row == 0 or i == len(items):
            keyboard.row()

    return keyboard.adjust(*sizes).as_markup()


async def format_poll_button(poll: Poll) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=poll.title,
        callback_data=f'pass_{poll.id}'
    )


async def format_user_button(user: User) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=user.phone,
        callback_data=f'patient_{user.id}'
    )


async def make_poll_inline_list(polls: List[Poll], sizes: tuple[int] = (3,)) -> ReplyKeyboardMarkup:
    return await create_inline_keyboard(polls, format_poll_button, 3, sizes)


async def make_patient_inline_keyboard(users: List[User], sizes: tuple[int] = (3,)) -> ReplyKeyboardMarkup:
    return await create_inline_keyboard(users, format_user_button, 3, sizes)


# async def make_poll_inline_list(
#         polls: List[Poll],
#         sizes: tuple[int] = (3,)
# ) -> ReplyKeyboardMarkup:
#     keyboard = InlineKeyboardBuilder()
#     buttons_per_row = 3
#
#     for i, poll in enumerate(polls, start=1):
#         button_text = poll.title
#         keyboard.add(InlineKeyboardButton(
#             text=button_text,
#             callback_data=f'pass_{poll.id}')
#         )
#
#         if i % buttons_per_row == 0 or i == len(polls):
#             keyboard.row()  # Переход на новую строку после добавления кнопок
#
#     return keyboard.adjust(*sizes).as_markup()
#
#
# async def make_patient_inline_keyboard(
#         users: List[User],
#         sizes: tuple[int] = (3,)
# ) -> ReplyKeyboardMarkup:
#     keyboard = InlineKeyboardBuilder()
#     buttons_per_row = 3
#
#     for i, user in enumerate(users, start=1):
#         button_text = user.phone
#         keyboard.add(InlineKeyboardButton(
#             text=button_text,
#             callback_data=f'patient_{user.id}')
#         )
#
#         if i % buttons_per_row == 0 or i == len(users):
#             keyboard.row()
#
#     return keyboard.adjust(*sizes).as_markup()


async def make_psy_poll_inline_list(psy_id: int) -> ReplyKeyboardMarkup:
    poll_list = await get_owner_user_polls(psy_id)

    return await make_poll_inline_list(poll_list)


async def delete_button_with_builder_preserve_rows(
        keyboard: InlineKeyboardMarkup,
        callback_data: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for row in keyboard.inline_keyboard:
        filtered_row = [
            button for button in row
            if button.callback_data != callback_data
        ]

        if filtered_row:
            builder.row(*filtered_row)

    return builder.as_markup()
