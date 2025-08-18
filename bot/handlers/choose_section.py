from ..helpers import nav_set_section, get_db
from ..keyboards import generate_section_filters_keyboard_dynamic, LABEL_TO_SECTION

async def handle_choose_section(update, context, text):
    if text not in LABEL_TO_SECTION:
        return None
    section_code = LABEL_TO_SECTION[text]
    nav_set_section(context.user_data, text, section_code)
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    db = get_db(context)
    years = await db.get_years_for_subject_section(subject_id, section_code)
    lecturers = await db.get_lecturers_for_subject_section(subject_id, section_code)
    lectures_exist = await db.has_lecture_category(subject_id, section_code)
    return await update.message.reply_text(
        "اختر طريقة التصفية:",
        reply_markup=generate_section_filters_keyboard_dynamic(bool(years), bool(lecturers), lectures_exist),
    )
