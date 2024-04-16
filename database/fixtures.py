from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Role, AnswerType, Poll, Question, AnswerOption

polls_data = [
    {'id': 2, 'title': 'Опрос о стрессе', 'description': 'Опрос для измерения уровня стресса',
     'psychologist_id': 305502452},
    {'id': 3, 'title': 'Опрос о семейных отношениях', 'description': 'Опрос о качестве семейных отношений',
     'psychologist_id': 305502452},
    {'id': 4, 'title': 'Опрос о самооценке', 'description': 'Опрос для оценки уровня самооценки',
     'psychologist_id': 305502452},
    {'id': 5, 'title': 'Опрос о мотивации', 'description': 'Опрос для изучения мотивации личности',
     'psychologist_id': 305502452},
]
questions_data = [
    {
        'poll_id': 2,
        'text': 'Что вызывает у вас наибольший уровень стресса?',
        'answer_options': [
            {'value': 'Работа'},
            {'value': 'Семейные отношения'},
            {'value': 'Финансовые проблемы'},
            {'value': 'Здоровье'},
            {'value': 'Другое'},
        ],
        'answer_type': 'test'
    },
    {
        'poll_id': 2,
        'text': 'Как вы обычно справляетесь со стрессом?',
        'answer_options': [
            {'value': 'Спорт или физическая активность'},
            {'value': 'Медитация и релаксация'},
            {'value': 'Разговор с близкими'},
            {'value': 'Поиск профессиональной помощи'},
            {'value': 'Другие методы'},
        ],
        'answer_type': 'test'
    },
    {
        'poll_id': 3,
        'text': 'Как часто вы общаетесь с членами вашей семьи?',
        'answer_options': [
            {'value': 'Ежедневно'},
            {'value': 'Несколько раз в неделю'},
            {'value': 'Редко'},
            {'value': 'Почти никогда'},
        ],
        'answer_type': 'test'
    },
    {
        'poll_id': 3,
        'text': 'Как часто вы сравниваете себя с другими людьми?',
        'answer_options': [
            {'value': 'Почти всегда'},
            {'value': 'Иногда'},
            {'value': 'Редко'},
            {'value': 'Почти никогда'},
        ],
        'answer_type': 'test'
    },
    {
        'poll_id': 4,
        'text': 'Что для вас является наиболее важным в карьере?',
        'answer_options': [
            {'value': 'Достижение успеха и признания'},
            {'value': 'Интересная и творческая работа'},
            {'value': 'Стабильность и материальное благополучие'},
            {'value': 'Социальная значимость и помощь другим'},
        ],
        'answer_type': 'test'
    },
    {
        'poll_id': 4,
        'text': 'Как часто вы испытываете чувство усталости и безысходности?',
        'answer_options': [
            {'value': 'Почти каждый день'},
            {'value': 'Несколько раз в неделю'},
            {'value': 'Иногда'},
            {'value': 'Редко'},
        ],
        'answer_type': 'test'
    },
    {
        'poll_id': 4,
        'text': 'Что для вас является основным источником счастья?',
        'answer_options': [
            {'value': 'Любовь и отношения'},
            {'value': 'Достижение жизненных целей'},
            {'value': 'Материальное благополучие'},
            {'value': 'Саморазвитие и самоопределение'},
        ],
        'answer_type': 'test'
    },
    {
        'poll_id': 4,
        'text': 'Как часто вы испытываете чувство тревоги или неопределенности в будущем?',
        'answer_type': 'free'
    },
]


async def add_roles(session: AsyncSession) -> None:
    admin_role = Role(slug='admin', name='Администратор', description='Роль администратора')
    psychologist_role = Role(slug='psychologist', name='Психолог', description='Роль психолога')
    user_role = Role(slug='patient', name='Пользователь', description='Роль обычного пользователя')

    #session.add_all([admin_role, psychologist_role, user_role])
    #await session.commit()


async def add_answer_types(session: AsyncSession) -> None:
    free_answer = AnswerType(slug='free', name='Свободный ответ', description='Свободный текстовый ответ')
    test_answer = AnswerType(slug='test', name='С вариантами ответа', description='Фиксированные варианты ответов')

    #session.add_all([free_answer, test_answer])
    #await session.commit()


async def add_polls(session: AsyncSession) -> None:
    for poll_data in polls_data:
        poll = Poll(**poll_data)
        # session.add(poll)
    # await session.commit()


async def add_questions(session: AsyncSession) -> None:
    for question_data in questions_data:
        question = Question(
            text=question_data['text'],
            poll_id=question_data['poll_id'],
            answer_type=question_data['answer_type'],

        )
        # session.add(question)
        answer_options = question_data.get('answer_options', [])
        if answer_options:
            for option_data in question_data['answer_options']:
                option = AnswerOption(value=option_data['value'], question_id=question.id)
                # session.add(option)

    # await session.commit()