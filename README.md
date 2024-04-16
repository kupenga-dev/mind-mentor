aiogram 3.4.1 + sqlalchemy 2
````
Table "users" as User {
  id Bigint [pk]
  created DateTime
  updated DateTime
  fio String(150)
  phone String(30) [unique]
  chat_id bigint
}

Table "roles" as Role {
  id Bigint [pk]
  created DateTime
  updated DateTime
  slug String(30)
  name String(80)
  description String(120)
}

Table "user_roles" as UserRole {
  id Bigint [pk]
  created DateTime
  updated DateTime
  user_id Bigint [ref: > User.id]
  role_id Bigint [ref: > Role.id]
}

Table "polls" as Poll {
  id Bigint [pk]
  created DateTime
  updated DateTime
  psychologist_id Bigint [ref: > User.id]
  title String(100)
  description Text
}

Table "questions" as Question {
  id Bigint [pk]
  created DateTime
  updated DateTime
  text Text
  poll_id Bigint [ref: > Poll.id]
  answer_type String(80) [ref: > AnswerType.slug]
}

Table "answer_options" as AnswerOption {
  id Bigint [pk]
  created DateTime
  updated DateTime
  value String(100)
  question_id Bigint [ref: > Question.id]
}

Table "answer_types" as AnswerType {
  id Bigint [pk]
  created DateTime
  updated DateTime
  name String(80)
  slug String(80) [unique]
  description Text
}

Table "answers" as Answer {
  id Bigint [pk]
  created DateTime
  updated DateTime
  user_id Bigint [ref: > User.id]
  poll_id Bigint [ref: > Poll.id]
  question_id Bigint [ref: > Question.id]
  text Text
}

Table "poll_availability" as PollAvailability {
  id Bigint [pk]
  created DateTime
  updated DateTime
  poll_id Bigint [ref: > Poll.id]
  user_id Bigint [ref: > User.id]
}
````