import phonenumbers
from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from phonenumbers import PhoneNumberFormat

from common.cmd_list import get_role_keyboard
from database.requests import register
from enums.enums import RoleRusEnum, RoleSlugEnum, BaseEnum
from filters.chat_types import ChatTypeFilter, IsUnAuthorized
from filters.state_filters import is_correct_phone_number, has_user_with_this_phone_number
from keyboards.reply import KeyboardBuilder

register_router = Router()
register_router.message.filter(ChatTypeFilter(['private']), IsUnAuthorized())
keyboard_builder = KeyboardBuilder()


class Register(StatesGroup):
    fio = State()
    phone = State()
    role = State()

    texts = {
        'Register:fio': 'Введите ФИО:',
        'Register:phone': 'Введите телефон:',
        'Register:role': 'Выберите роль:',
    }


@register_router.message(StateFilter(None), F.text.lower() == 'регистрация')
async def register_start(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Введите фио:", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Register.fio)


@register_router.message(Register.fio, F.text)
async def add_fio(message: types.Message, state: FSMContext) -> None:
    if len(message.text) >= 100:
        await message.answer("ФИО не должно превышать 100 символов. \n Введите заново")
        return

    await state.update_data(fio=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(Register.phone)


@register_router.message(Register.phone, F.text)
async def add_phone(message: types.Message, state: FSMContext) -> None:
    is_correct_phone = await is_correct_phone_number(message.text)
    if not is_correct_phone:
        await message.answer(
            'Неправильный формат номера. Пожалуйста, введите номер заново.'
        )
        return

    number = phonenumbers.parse(message.text, 'RU')
    formatted_number = phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)

    is_present_user = await has_user_with_this_phone_number(formatted_number)

    if is_present_user:
        await message.answer(
            'Пользователя с таким номером телефона уже существует. Пожалуйста, введите номер заново.'
        )
        return

    await state.update_data(phone=formatted_number)
    role_keyboard = await keyboard_builder.make_role_keyboard()
    await message.answer("Выберите роль", reply_markup=role_keyboard)
    await state.set_state(Register.role)


@register_router.message(Register.role, F.text)
async def add_role(message: types.Message, state: FSMContext) -> None:
    role_attr = BaseEnum.get_attribute_by_value(RoleRusEnum, message.text.lower())

    if role_attr is None:
        return

    role_slug_value = getattr(RoleSlugEnum, role_attr.name, None)
    if role_slug_value is None:
        return

    await state.update_data(role=role_slug_value.value)
    data = await state.get_data()
    await register(data, message.from_user.id, message.chat.id)
    await state.clear()
    role_keyboard = await get_role_keyboard(role_slug_value.value)
    await message.answer("Регистрация прошла успешно.", reply_markup=role_keyboard)
