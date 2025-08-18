from ..keyboards import generate_lecture_titles_keyboard
from ..helpers import get_db

async def render_lecture_list(update, context):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    year_id = nav.get("data", {}).get("year_id")
    lecturer_id = nav.get("data", {}).get("lecturer_id")

    db = get_db(context)
    titles = await db.list_lecture_titles(subject_id, section_code)
    heading = "اختر محاضرة:"

    if year_id and lecturer_id:
        titles = await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id)
        heading = "اختر محاضرة (محاضر + سنة):"
    elif lecturer_id:
        titles = await db.list_lecture_titles_by_lecturer(subject_id, section_code, lecturer_id)
        heading = "اختر محاضرة (حسب المحاضر):"
    elif year_id:
        titles = await db.list_lecture_titles_by_year(subject_id, section_code, year_id)
        heading = "اختر محاضرة (حسب السنة):"

    msg = heading if titles else "لا توجد محاضرات مطابقة."
    return await update.message.reply_text(msg, reply_markup=generate_lecture_titles_keyboard(titles))
