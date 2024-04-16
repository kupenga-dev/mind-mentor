from datetime import datetime
from typing import Sequence, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from database.engine import session_maker
from database.models import User, UserRole, Role, Poll, PollAvailability
from enums.enums import RoleSlugEnum


async def find_user_by_phone(phone: str) -> User | None:
    user_stm = (
        select(User)
        .filter(User.phone == phone)
    )
    async with session_maker() as session:
        user = await session.execute(user_stm)

    return user.scalar_one_or_none()


async def find_patients_by_psy_id(psy_id: int) -> List[User] | None:
    patient_smt = (
        select(User)
        .join(PollAvailability, PollAvailability.user_id == User.id)
        .filter(PollAvailability.psy_id == psy_id)
    )
    async with session_maker() as session:
        try:
            result = await session.execute(patient_smt)
            patients = result.scalars().all()
            return patients if patients else None
        except Exception as e:
            print(f"Error fetching patients: {e}")
            return None


async def insert(
        user: Dict[str, Any],
        tg_id: int,
        chat_id: int
) -> None:
    current_time = datetime.now()
    user = User(
        id=tg_id,
        fio=user['fio'],
        chat_id=chat_id,
        phone=user['phone'],
        created=current_time,
        updated=current_time
    )

    async with session_maker() as session:
        session.add(user)
        await session.commit()


class UserRepo:
    def __init__(self):
        pass

    async def get_users_by_role(self, user_id: int) -> List[User]:
        role_slug = self.get_user_role(user_id)

        return await self.__get_user_list() \
            if role_slug == RoleSlugEnum.ADMIN \
            else await self.__get_patient_list(user_id)

    async def get_user_role(self, user_id: int) -> str:
        user_role_stm = (
            select(Role.slug)
            .join(UserRole, Role.id == UserRole.role_id)
            .filter(UserRole.user_id == user_id)
        )
        async with session_maker() as session:
            user_role = await session.execute(user_role_stm)

            user_role_row = user_role.scalar_one_or_none()

            return user_role_row if user_role_row else None

    async def __get_user_list(self) -> Sequence[User]:
        users_stm = select(User)
        async with session_maker() as session:
            users = await session.execute(users_stm)

            return users.scalars().all()

    async def __get_patient_list(self, user_id: int) -> List[User]:
        patients_smt = (
            select(User)
            .join(Poll, User.id == Poll.psychologist_id)
            .filter(Poll.id == user_id)
        )
        async with session_maker() as session:
            patients = await session.execute(patients_smt)

            return list(patients.scalars().all())

    async def is_unauthorized(self, user_id: int) -> bool:
        stmt = select(User).filter(User.id == user_id)

        try:
            async with session_maker() as session:
                result = await session.execute(stmt)
                user = result.scalars().first()

            if user:
                return False
        except NoResultFound:
            pass

        return True

    async def insert(self, user: Dict[str, Any], tg_id: int, chat_id: int) -> None:
        current_time = datetime.now()

        user = User(
            id=tg_id,
            fio=user['fio'],
            chat_id=chat_id,
            phone=user['phone'],
            created=current_time,
            updated=current_time
        )
        async with session_maker() as session:
            session.add(user)
            await session.commit()
