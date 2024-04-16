import asyncio
import os

import aioschedule
from aiogram import Bot, Dispatcher, types

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from common.cmd_list import private
from states.create_poll import create_poll_router
from states.pass_poll import pass_poll_router
from database.engine import check_and_fill_db
from handlers.system import system_router
from handlers.user import user_router
from handlers.psychologist import psychologist_router
from handlers.state import state_router
from states.register import register_router
from notifications.base import poll_not_passed_notification
from states.give_poll_access import give_poll_access_router


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()
dp.include_routers(
    register_router,
    state_router,
    pass_poll_router,
    user_router,
    psychologist_router,
    create_poll_router,
    give_poll_access_router,
    system_router,
)


async def scheduler() -> None:
    aioschedule.every().day.at("20:00pyh").do(poll_not_passed_notification, bot)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main() -> None:
    await check_and_fill_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())

    asyncio.create_task(scheduler())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
