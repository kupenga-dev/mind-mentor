from aiogram import types, Router, F
from aiogram.filters import CommandStart

from common.cmd_list import SYSTEM_KB, get_keyboard_by_id
from filters.chat_types import ChatTypeFilter

system_router = Router()
system_router.message.filter(ChatTypeFilter(['private']))


@system_router.message(CommandStart())
async def start(message: types.Message) -> None:
    await message.answer(
        'Выберите команду:', reply_markup=SYSTEM_KB
    )


@system_router.message(F.text.lower() == 'о нас')
async def about(message: types.Message) -> None:
    role_keyboard = await get_keyboard_by_id(message.from_user.id)
    await message.answer(
        'Данный бот помогает автоматизировать работу психологов.',
        reply_markup=role_keyboard
    )


@system_router.message(F.photo | F.sticker)
async def error(message: types.Message) -> None:
    role_keyboard = await get_keyboard_by_id(message.from_user.id)
    await message.answer(
        'Бот работает только с текстовыми командами.',
        reply_markup=role_keyboard
    )


@system_router.message(F.text)
async def handle_unexpected_messages(message: types.Message) -> None:
    role_keyboard = await get_keyboard_by_id(message.from_user.id)
    await message.answer(
        "Извините, я не понимаю вашего сообщения. "
        "\nПожалуйста, используйте доступные варианты.",
        reply_markup=role_keyboard
    )

