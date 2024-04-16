from enum import Enum


class BaseEnum(Enum):
    @staticmethod
    def get_attribute_by_value(enum_class, value):
        for name, member in enum_class.__members__.items():
            if member.value == value:
                return member
        return None


class RoleSlugEnum(BaseEnum):
    ADMIN = 'admin'
    PSYCHOLOGIST = 'psychologist'
    USER = 'patient'


class RoleRusEnum(BaseEnum):
    ADMIN = 'администратор'
    PSYCHOLOGIST = 'психолог'
    USER = 'пользователь'


class AnswerTypeRusEnum(BaseEnum):
    FREE = 'свободный ответ'
    TEST = 'c вариантами ответа'


class AnswerTypeSlug(BaseEnum):
    FREE = 'free'
    TEST = 'test'
