from aiogram import Bot

from database.requests import get_user_chat_id_with_not_passed_polls


async def poll_not_passed_notification(bot: Bot) -> None:
    not_passed_notifications = await get_user_chat_id_with_not_passed_polls()

    for chat_id, poll_title in not_passed_notifications:
        await bot.send_message(chat_id, f"Привет! У тебя есть непройденный опрос: {poll_title}")
