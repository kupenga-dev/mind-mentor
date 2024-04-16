from aiogram import Router, F, types

from common.cmd_list import get_keyboard_by_id
from filters.chat_types import ChatTypeFilter, IsUser

user_router = Router()
user_router.message.filter(ChatTypeFilter(['private']), IsUser())


@user_router.message(F.text.lower() == 'об опросах')
async def poll_info(message: types.Message) -> None:
    role_keyboard = await get_keyboard_by_id(message.from_user.id)

    await message.answer(
        'Вам нужно попросить психолога внести ваш телефон в список.',
        reply_markup=role_keyboard
    )
