import io

from openpyxl import Workbook


async def generate_excel_report(rows) -> io.BytesIO:
    file_data = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.append(['ФИО', 'Телефон', 'Ответ', 'Вопрос', 'Дата ответа'])

    for row in rows:
        row_values = [
            row[0],
            row[1],
            row[2],
            row[3],
            row[4]
        ]
        ws.append(row_values)

    wb.save(file_data)
    file_data.seek(0)

    return file_data
