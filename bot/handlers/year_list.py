from ..db import get_years_for_subject_section, get_years_for_subject_section_lecturer
from ..keyboards import generate_years_keyboard

async def render_year_list(update, context):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    lecturer_id = nav.get("data", {}).get("lecturer_id")
    if lecturer_id:
        years = await get_years_for_subject_section_lecturer(subject_id, section_code, lecturer_id)
        msg = "اختر السنة (للمحاضر المحدد):"
    else:
        years = await get_years_for_subject_section(subject_id, section_code)
        msg = "اختر السنة:"
    return await update.message.reply_text(msg, reply_markup=generate_years_keyboard(years))
