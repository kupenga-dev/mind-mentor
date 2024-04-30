from aiogram import Router, F, types
from aiogram.types import BufferedInputFile

from common.cmd_list import get_keyboard_by_id
from common.files import generate_excel_report
from database.requests import collect_polls_info_by_psy, collect_history_by_patient
from filters.chat_types import ChatTypeFilter, IsPsychologist
from keyboards.inline import make_patient_inline_keyboard
from repo.user_repo import find_patients_by_psy_id

psychologist_router = Router()
psychologist_router.message.filter(ChatTypeFilter(['private']), IsPsychologist())


@psychologist_router.message(F.text.lower() == 'получить историю опросов')
async def take_info(message: types.Message) -> None:
    history = await collect_polls_info_by_psy(message.from_user.id)
    report_file = await generate_excel_report(history)

    report_input_file = BufferedInputFile(
        report_file.getvalue(),
        filename='polls_report.xlsx'
    )

    await message.answer_document(report_input_file)


@psychologist_router.message(F.text.lower() == 'получить историю по клиенту')
async def take_patient_list(message: types.Message) -> None:
    patients = await find_patients_by_psy_id(message.from_user.id)
    if patients is None:
        role_keyboard = await get_keyboard_by_id(message.from_user.id)

        await message.answer(
            'У вас нет действующих клиентов.',
            reply_markup=role_keyboard
        )
        return

    keyboard = await make_patient_inline_keyboard(patients)

    await message.answer(
        'Выберите клиента.',
        reply_markup=keyboard
    )


@psychologist_router.callback_query(F.data.startswith('patient_'))
async def take_patient_history(callback: types.CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])
    history = await collect_history_by_patient(user_id, callback.from_user.id)
    report_file = await generate_excel_report(history)

    report_input_file = BufferedInputFile(
        report_file.getvalue(),
        filename=f'history_user_{user_id}.xlsx'
    )

    await callback.message.answer_document(report_input_file)
