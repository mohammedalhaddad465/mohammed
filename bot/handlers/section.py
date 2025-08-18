from ..db import (
    get_years_for_subject_section,
    get_lecturers_for_subject_section,
    has_lecture_category,
)
from ..keyboards import generate_section_filters_keyboard_dynamic

async def render_section(update, context):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    years = await get_years_for_subject_section(subject_id, section_code)
    lecturers = await get_lecturers_for_subject_section(subject_id, section_code)
    lectures_exist = await has_lecture_category(subject_id, section_code)
    return await update.message.reply_text(
        "اختر طريقة التصفية:",
        reply_markup=generate_section_filters_keyboard_dynamic(bool(years), bool(lecturers), lectures_exist),
    )
