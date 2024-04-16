from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from common.cmd_list import get_keyboard_by_id
from database.requests import create_poll
from filters.chat_types import ChatTypeFilter, IsPsychologist
from filters.state_filters import is_yes_no_answers, is_correct_answer_type
from keyboards.reply import KeyboardBuilder

create_poll_router = Router()
create_poll_router.message.filter(ChatTypeFilter(['private']), IsPsychologist())
question_index = 0
option_index = 0


class CreatePoll(StatesGroup):
    title = State()
    description = State()

    class Questions(StatesGroup):
        name = State()
        answer_type = State()
        one_more = State()

        class Answer(StatesGroup):
            one_more = State()
            answer_options = State()

    texts = {
        'CreatePoll:title': 'Введите название опроса:',
        'CreatePoll:description': 'Введите описание опроса:',
        'CreatePoll:Questions.name': 'Введите вопросы для опроса:',
        'CreatePoll:Questions.answer_type': 'Введите тип вопроса:',
        'CreatePoll:Answer.answer_type': 'Введите тип вопроса:',
    }


async def save_db(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await create_poll(data, message.from_user.id)
    role_keyboard = await get_keyboard_by_id(message.from_user.id)
    await message.answer(
        "Данные опроса собраны. Опрос создан",
        reply_markup=role_keyboard
    )


async def take_question_name(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get('questions', [])
    questions.insert(question_index, {'name': message.text})
    await state.update_data(questions=questions)


async def take_question_type(state: FSMContext, slug: str) -> None:
    data = await state.get_data()
    questions = data.get('questions', [])
    questions[question_index].update({'answer_type': slug})
    await state.update_data(questions=questions)


async def take_answer_option(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get('questions', [])
    question_info = questions.__getitem__(question_index)
    if 'options' in question_info:
        question_info['options'].update({option_index: message.text})
    else:
        question_info['options'] = {option_index: message.text}


async def ask_more_questions(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Хотите добавить еще один вопрос?",
        reply_markup=KeyboardBuilder().make_yes_no_keyboard()
    )
    await state.set_state(CreatePoll.Questions.one_more)


async def ask_more_options(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Хотите добавить еще один ответ?",
        reply_markup=KeyboardBuilder().make_yes_no_keyboard()
    )
    await state.set_state(CreatePoll.Questions.Answer.one_more)


@create_poll_router.message(StateFilter(None), F.text.lower() == 'создать опрос')
async def poll_title(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Введите название опроса:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(CreatePoll.title)


@create_poll_router.message(CreatePoll.title, F.text)
async def poll_description(message: types.Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await message.answer(
        "Введите описание опроса:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(CreatePoll.description)


@create_poll_router.message(CreatePoll.description, F.text)
async def start_question_input(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await message.answer(
        "Введите вопрос:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(CreatePoll.Questions.name)


@create_poll_router.message(CreatePoll.Questions.name, F.text)
async def question_input(message: types.Message, state: FSMContext) -> None:
    await take_question_name(message, state)

    keyboard_builder = KeyboardBuilder()
    answer_type_keyboard = await keyboard_builder.make_answer_types_keyboard()
    await message.answer(
        "Выберите тип вопроса:",
        reply_markup=answer_type_keyboard
    )
    await state.set_state(CreatePoll.Questions.answer_type)


@create_poll_router.message(StateFilter(CreatePoll.Questions.answer_type), F.text)
async def test_answer_poll(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'с вариантами ответа':
        await take_question_type(state, 'test')
        await message.answer(
            "Введите вариант ответа:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(CreatePoll.Questions.Answer.answer_options)
    else:
        await take_question_type(state, 'free')
        await ask_more_questions(message, state)


@create_poll_router.message(StateFilter(CreatePoll.Questions.one_more), F.text)
async def one_more_question(message: types.Message, state: FSMContext) -> None:
    is_correct_answer = await is_yes_no_answers(message.text.lower())
    if not is_correct_answer:
        await message.answer(
            'Пожалуйста, ответьте да или нет.',
            reply_markup=KeyboardBuilder().make_yes_no_keyboard()
        )

        await state.set_state(CreatePoll.Questions.one_more)
        return

    global question_index
    if message.text.lower() == 'да':
        question_index += 1
        await message.answer(
            "Введите ещё один вопрос:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(CreatePoll.Questions.name)
    else:
        question_index = 0
        await save_db(message, state)


@create_poll_router.message(StateFilter(CreatePoll.Questions.Answer.answer_options), F.text)
async def input_answer_option(message: types.Message, state: FSMContext) -> None:
    await take_answer_option(message, state)
    await ask_more_options(message, state)


@create_poll_router.message(StateFilter(CreatePoll.Questions.Answer.one_more), F.text)
async def more_options(message: types.Message, state: FSMContext) -> None:
    is_correct_answer = await is_yes_no_answers(message.text.lower())
    if not is_correct_answer:
        await message.answer(
            'Пожалуйста, ответьте да или нет.',
            reply_markup=KeyboardBuilder().make_yes_no_keyboard()
        )
        await more_options(message, state)
        return

    global option_index
    if message.text.lower() == 'да':
        option_index += 1
        await message.answer(
            "Введите ещё один ответ:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(CreatePoll.Questions.Answer.answer_options)
    else:
        option_index = 0
        await ask_more_questions(message, state)
