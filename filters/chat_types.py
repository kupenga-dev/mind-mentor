from aiogram.filters import Filter
from aiogram import types, Bot

from repo.role_repo import RoleRepo
from repo.user_repo import UserRepo


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


class BaseRoleFilter(Filter):
    def __init__(self, role_check_func: callable):
        self.role_check_func = role_check_func

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        role_repo = RoleRepo()

        return await self.role_check_func(role_repo, message.from_user.id)


class IsPsychologist(BaseRoleFilter):
    def __init__(self):
        super().__init__(RoleRepo.is_psychologist)

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return await super().__call__(message, bot)


class IsAdmin(BaseRoleFilter):
    def __init__(self):
        super().__init__(RoleRepo.is_admin)

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return await super().__call__(message, bot)


class IsUser(BaseRoleFilter):
    def __init__(self):
        super().__init__(RoleRepo.is_user)

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return await super().__call__(message, bot)


class IsUnAuthorized(Filter):
    def __init__(self):
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        user_repo = UserRepo()

        return await user_repo.is_unauthorized(message.from_user.id)
