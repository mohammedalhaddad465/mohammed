from ..helpers import nav_set_section
from ..db import (
    get_years_for_subject_section,
    get_lecturers_for_subject_section,
    has_lecture_category,
)
from ..keyboards import generate_section_filters_keyboard_dynamic, LABEL_TO_SECTION

async def handle_choose_section(update, context, text):
    if text not in LABEL_TO_SECTION:
        return None
    section_code = LABEL_TO_SECTION[text]
    nav_set_section(context.user_data, text, section_code)
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    years = await get_years_for_subject_section(subject_id, section_code)
    lecturers = await get_lecturers_for_subject_section(subject_id, section_code)
    lectures_exist = await has_lecture_category(subject_id, section_code)
    return await update.message.reply_text(
        "اختر طريقة التصفية:",
        reply_markup=generate_section_filters_keyboard_dynamic(bool(years), bool(lecturers), lectures_exist),
    )
