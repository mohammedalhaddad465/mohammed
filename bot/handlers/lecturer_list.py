from ..db import get_lecturers_for_subject_section
from ..keyboards import generate_lecturers_keyboard

async def render_lecturer_list(update, context):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    lecturers = await get_lecturers_for_subject_section(subject_id, section_code)
    return await update.message.reply_text("اختر المحاضر:", reply_markup=generate_lecturers_keyboard(lecturers))
