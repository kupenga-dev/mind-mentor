from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from common.cmd_list import get_keyboard_by_id
from filters.chat_types import ChatTypeFilter

state_router = Router()
state_router.message.filter(ChatTypeFilter(['private']))


@state_router.message(StateFilter('*'), Command("cancel"))
@state_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    role_keyboard = await get_keyboard_by_id(message.from_user.id)
    await message.answer(
        "Действия отменены",
        reply_markup=role_keyboard
    )
