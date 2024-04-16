from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from database.engine import session_maker
from database.models import Role, UserRole
from enums.enums import RoleSlugEnum


async def attach(user_id: int, role_slug: str) -> None:
    role_id = await get_id_by_slug(role_slug)
    current_time = datetime.now()

    if role_id is None:
        return

    user_role = UserRole(
        user_id=user_id,
        role_id=role_id,
        created=current_time,
        updated=current_time
    )
    async with session_maker() as session:
        session.add(user_role)
        await session.commit()


async def get_id_by_slug(slug: str) -> int | None:
    stmt = select(Role).filter(Role.slug == slug)
    async with session_maker() as session:
        role = await session.execute(stmt)
        role_obj = role.scalars().first()

    if not role_obj:
        return None

    return role_obj.id


class RoleRepo:
    def __init__(self):
        pass

    async def get(self) -> List[Role]:
        role_smt = select(Role)
        async with session_maker() as session:
            roles = await session.execute(role_smt)

            return list(roles.scalars().all())

    async def __has_role(self, user_id: int, role_slug: str) -> bool:
        stmt = (
            select(Role.slug)
            .select_from(UserRole)
            .join(Role)
            .where(UserRole.user_id == user_id)
        )

        try:
            async with session_maker() as session:
                result = await session.execute(stmt)
                user_role_slug = result.scalars().first()

            if user_role_slug == role_slug:
                return True
        except NoResultFound:
            pass

        return False

    async def is_admin(self, user_id: int) -> bool:
        return await self.__has_role(user_id, RoleSlugEnum.ADMIN.value)

    async def is_psychologist(self, user_id: int) -> bool:
        return await self.__has_role(user_id, RoleSlugEnum.PSYCHOLOGIST.value)

    async def is_user(self, user_id: int) -> bool:
        return await self.__has_role(user_id, RoleSlugEnum.USER.value)

    async def __get_id_by_slug(self, slug: str) -> int | None:
        stmt = select(Role).filter(Role.slug == slug)
        async with session_maker() as session:
            role = await session.execute(stmt)
            role_obj = role.scalars().first()

        if not role_obj:
            return None

        return role_obj.id

    async def attach(self, user_id: int, role_slug: str) -> None:
        role_id = await self.__get_id_by_slug(role_slug)
        current_time = datetime.now()

        if role_id is None:
            return

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            created=current_time,
            updated=current_time
        )
        async with session_maker() as session:
            session.add(user_role)
            await session.commit()
