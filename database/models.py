from sqlalchemy import DateTime, func, String, ForeignKey, Text, UniqueConstraint, Column, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(BaseModel):
    __tablename__ = 'users'

    fio: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    chat_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False, unique=True)


class Role(BaseModel):
    __tablename__ = 'roles'

    slug: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(120))


class UserRole(BaseModel):
    __tablename__ = 'user_roles'

    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'))
    role_id: Mapped[BigInteger] = mapped_column(ForeignKey('roles.id'))


class Poll(BaseModel):
    __tablename__ = 'polls'

    psychologist_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class Question(BaseModel):
    __tablename__ = 'questions'

    text: Mapped[str] = mapped_column(Text, nullable=False)
    poll_id: Mapped[BigInteger] = mapped_column(ForeignKey('polls.id'))
    answer_options = relationship('AnswerOption', back_populates='question')
    answer_type: Mapped[str] = mapped_column(ForeignKey('answer_types.slug'))


class AnswerOption(BaseModel):
    __tablename__ = 'answer_options'

    value: Mapped[str] = mapped_column(String(100), nullable=False)
    question_id: Mapped[BigInteger] = mapped_column(ForeignKey('questions.id'), nullable=False)
    question = relationship('Question', back_populates='answer_options')


class AnswerType(BaseModel):
    __tablename__ = 'answer_types'

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint('slug'),
    )


class Answer(BaseModel):
    __tablename__ = 'answers'

    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'), nullable=False)
    poll_id: Mapped[BigInteger] = mapped_column(ForeignKey('polls.id'), nullable=False)
    question_id: Mapped[BigInteger] = mapped_column(ForeignKey('questions.id'), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class PollAvailability(BaseModel):
    __tablename__ = 'poll_availability'

    poll_id: Mapped[BigInteger] = mapped_column(ForeignKey('polls.id'))
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'))
    psy_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'))
