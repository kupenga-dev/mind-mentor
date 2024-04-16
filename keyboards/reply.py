from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.models import AnswerOption
from repo.answer_type_repo import get
from repo.poll_repo import get_user_polls
from repo.role_repo import RoleRepo


class KeyboardBuilder:
    def __init__(self):
        pass

    async def make_role_keyboard(self) -> ReplyKeyboardMarkup:
        role_buttons = await self.__collect_role_buttons()

        return ReplyKeyboardMarkup(
            keyboard=[role_buttons],
            resize_keyboard=True,
            input_field_placeholder='Выберите роль'
        )

    async def make_answer_types_keyboard(self) -> ReplyKeyboardMarkup:
        answer_types_buttons = await self.__collect_answer_types_buttons()

        return ReplyKeyboardMarkup(
            keyboard=[answer_types_buttons],
            resize_keyboard=True,
            input_field_placeholder='Выберите тип ответа'
        )

    async def make_user_poll_list(self, user_id: int) -> ReplyKeyboardMarkup:
        poll_buttons = await self.__collect_poll_buttons(user_id)

        return ReplyKeyboardMarkup(
            keyboard=[poll_buttons],
            resize_keyboard=True,
            input_field_placeholder='Выберите опрос'
        )

    async def __collect_role_buttons(self) -> List[KeyboardButton]:
        role_repo = RoleRepo()
        roles = await role_repo.get()

        return [
            KeyboardButton(text=role.name)
            for role in roles
            if role.slug != 'admin'
        ]

    async def __collect_poll_buttons(self, user_id: int) -> List[KeyboardButton]:
        polls = await get_user_polls(user_id)

        return [
            KeyboardButton(text=poll.title)
            for poll in polls
        ]

    async def __collect_answer_types_buttons(self) -> List[KeyboardButton]:
        answer_types = await get()

        return [
            KeyboardButton(text=answer_type.name)
            for answer_type in answer_types
        ]

    @staticmethod
    def get_keyboard(
            *btns: str,
            placeholder: str = None,
            request_contact: int = None,
            request_location: int = None,
            sizes: tuple[int] = (2,),
    ) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardBuilder()

        for index, text in enumerate(btns, start=0):

            if request_contact and request_contact == index:
                keyboard.add(KeyboardButton(text=text, request_contact=True))

            elif request_location and request_location == index:
                keyboard.add(KeyboardButton(text=text, request_location=True))
            else:
                keyboard.add(KeyboardButton(text=text))

        return keyboard.adjust(*sizes).as_markup(
            resize_keyboard=True, input_field_placeholder=placeholder)

    @staticmethod
    def make_yes_no_keyboard() -> ReplyKeyboardMarkup:
        return KeyboardBuilder.get_keyboard(
            "Да",
            "Нет",
            placeholder="Выберите ответ:",
            sizes=(2,)
        )

    @staticmethod
    def make_poll_test_keyboard(answer_options: List[AnswerOption]) -> ReplyKeyboardMarkup:
        answer_buttons = [
            KeyboardButton(text=answer_option.value)
            for answer_option in answer_options
        ]

        return ReplyKeyboardMarkup(
            keyboard=[answer_buttons],
            resize_keyboard=True,
            input_field_placeholder='Выберите ответ'
        )
