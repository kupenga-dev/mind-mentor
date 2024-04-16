from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from common.cmd_list import get_keyboard_by_id
from database.models import Question
from database.requests import create_answers
from filters.chat_types import ChatTypeFilter, IsUser
from keyboards.inline import collect_user_poll_list
from keyboards.reply import KeyboardBuilder
from repo.poll_repo import get_poll_with_questions

pass_poll_router = Router()
pass_poll_router.message.filter(ChatTypeFilter(['private']), IsUser())
question_id = 0
index = 0


class PassPoll(StatesGroup):
    choose_poll = State()
    pass_question = State()

    texts = {
        'PassPoll:choose_poll': 'Выберите опрос:',
        'PassPoll:pass_poll': 'Введите ответ:',
    }


async def ask_question(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get('poll_questions', [])
    if questions:
        question = questions.pop(0)
        await state.update_data(poll_questions=questions)
        await choose_question(message, state, question)
    else:
        await save_poll(message, state)


async def choose_question(
        message: types.Message,
        state: FSMContext,
        question: Question
) -> None:
    global question_id
    question_id = question.id
    if question.answer_type == 'free':
        keyboard = types.ReplyKeyboardRemove()
    else:
        keyboard = KeyboardBuilder.make_poll_test_keyboard(question.answer_options)

    await message.answer(
        f"{question.text}",
        reply_markup=keyboard
    )
    await state.set_state(PassPoll.pass_question)


@pass_poll_router.message(StateFilter(None), F.text.lower() == 'мои опросы')
async def show_polls_from_history(message: types.Message, state: FSMContext) -> None:
    history_keyboard = await collect_user_poll_list(message.from_user.id)

    if history_keyboard is None:
        role_keyboard = await get_keyboard_by_id(message.from_user.id)
        await state.clear()
        await message.answer(
            "У вас нет доступных опросов.",
            reply_markup=role_keyboard
        )
    else:
        await message.answer(
            "Выберите опрос",
            reply_markup=history_keyboard
        )
        await state.set_state(PassPoll.choose_poll)


@pass_poll_router.callback_query(StateFilter(PassPoll.choose_poll), F.data.startswith('pass_'))
async def choose_poll(callback: types.CallbackQuery, state: FSMContext) -> None:
    poll_id = callback.data.split("_")[-1]
    poll_questions = await get_poll_with_questions(int(poll_id))
    await state.set_data({'poll_questions': poll_questions, 'poll_id': poll_id})
    await ask_question(callback.message, state)


@pass_poll_router.message(StateFilter(PassPoll.pass_question), F.text)
async def pass_poll_state(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    answers = data.get('answers', [])
    global question_id
    answers.append({'question_id': question_id, 'answer': message.text})
    await state.update_data(answers=answers)
    await ask_question(message, state)


async def save_poll(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    answers = data.get('answers', [])
    poll_id = data.get('poll_id', [])
    await state.clear()
    await create_answers(answers, message.from_user.id, poll_id)
    role_keyboard = await get_keyboard_by_id(message.from_user.id)
    await message.answer(
        "Опрос успешно пройден!",
        reply_markup=role_keyboard
    )
