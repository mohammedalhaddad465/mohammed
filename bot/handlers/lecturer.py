from ..keyboards import generate_lecturer_filter_keyboard
from ..helpers import get_db

async def render_lecturer(update, context):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    lecturer_label = nav.get("stack", [])[-1][1] if nav.get("stack") else ""
    lecturer_id = nav.get("data", {}).get("lecturer_id")
    db = get_db(context)
    years = await db.get_years_for_subject_section_lecturer(subject_id, section_code, lecturer_id)
    lectures_exist = await db.has_lecture_category(subject_id, section_code) or False
    return await update.message.reply_text(
        f"المحاضر: {lecturer_label}\nاختر خيارًا:",
        reply_markup=generate_lecturer_filter_keyboard(bool(years), lectures_exist),
    )
