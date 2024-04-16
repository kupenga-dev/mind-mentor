from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from common.cmd_list import get_keyboard_by_id
from database.requests import give_polls_access_to_user
from filters.chat_types import ChatTypeFilter, IsPsychologist
from filters.state_filters import is_correct_phone_number, has_user_with_this_phone_number, is_yes_no_answers
from keyboards.inline import make_psy_poll_inline_list, delete_button_with_builder_preserve_rows
from keyboards.reply import KeyboardBuilder

give_poll_access_router = Router()
give_poll_access_router.message.filter(ChatTypeFilter(['private']), IsPsychologist())


class GivePollAccess(StatesGroup):
    input_phone = State()
    choose_poll = State()
    choose_one_more_poll = State()

    texts = {
        'GivePollAccess:input_phone': 'Введите номер телефона:',
        'GivePollAccess:choose_poll': 'Выберите опрос:'
    }


async def ask_more_poll(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = data.get('keyboard')
    used_button = data.get('polls')[-1]
    rebuilding_keyboard = await delete_button_with_builder_preserve_rows(
        keyboard, used_button
    )

    await state.update_data(keyboard=rebuilding_keyboard)
    await message.answer(
        'Выберите опрос:',
        reply_markup=rebuilding_keyboard
    )


async def finish(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    phone = data.get('phone', '')
    polls = data.get('polls', [])

    await give_polls_access_to_user(phone, polls, message.from_user.id)
    role_keyboard = await get_keyboard_by_id(message.from_user.id)
    await message.answer(
        'Данные собраны.',
        reply_markup=role_keyboard
    )


@give_poll_access_router.message(StateFilter(None), F.text.lower() == 'дать доступ к опросу')
async def give_access_to_poll(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        'Введите номер телефона',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(GivePollAccess.input_phone)


@give_poll_access_router.message(GivePollAccess.input_phone, F.text)
async def input_phone(message: types.Message, state: FSMContext) -> None:
    is_correct_phone = await is_correct_phone_number(message.text)
    if not is_correct_phone:
        await message.answer(
            'Неправильный формат номера. Пожалуйста, введите номер заново.'
        )
        return

    has_user = await has_user_with_this_phone_number(message.text)

    if not has_user:
        await message.answer(
            'Пользователя с таким номером телефона не существует.'
        )
        return

    await state.update_data(phone=message.text)
    keyboard = await make_psy_poll_inline_list(message.from_user.id)
    if not keyboard:
        role_keyboard = await get_keyboard_by_id(message.from_user.id)
        await message.answer(
            'У вас пока нет созданных опросов.',
            reply_markup=role_keyboard
        )
        return

    await message.answer(
        'Выберите опрос:',
        reply_markup=keyboard
    )
    await state.update_data(keyboard=keyboard)
    await state.set_state(GivePollAccess.choose_poll)


@give_poll_access_router.callback_query(
    StateFilter(GivePollAccess.choose_poll),
    F.data.startswith('pass_')
)
async def input_poll(callback: types.CallbackQuery, state: FSMContext) -> None:
    poll_id = int(callback.data.split("_")[-1])

    data = await state.get_data()
    polls = data.get('polls', [])
    polls.append(poll_id)

    await state.update_data(polls=polls)
    await callback.message.answer(
        'Дать ещё к какому-то опросу доступ?',
        reply_markup=KeyboardBuilder().make_yes_no_keyboard()
    )
    await state.set_state(GivePollAccess.choose_one_more_poll)


@give_poll_access_router.message(StateFilter(GivePollAccess.choose_one_more_poll), F.text)
async def choose_one_more_poll(message: types.Message, state: FSMContext) -> None:
    is_correct_answer = await is_yes_no_answers(message.text.lower())
    if not is_correct_answer:
        await message.answer(
            'Пожалуйста, ответьте да или нет.',
            reply_markup=KeyboardBuilder().make_yes_no_keyboard()
        )

        await choose_one_more_poll(message, state)

    if message.text.lower() == 'нет':
        await finish(message, state)
        return

    await ask_more_poll(message, state)
