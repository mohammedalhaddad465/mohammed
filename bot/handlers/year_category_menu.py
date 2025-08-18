from ..keyboards import generate_year_category_menu_keyboard
from ..helpers import get_db

async def render_year_category_menu(update, context):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    year_id = nav.get("data", {}).get("year_id")
    lecturer_id = nav.get("data", {}).get("lecturer_id")
    if not year_id:
        from ..main import render_state
        return await render_state(update, context)
    db = get_db(context)
    if lecturer_id:
        lectures_exist = bool(await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id))
        cats = await db.list_categories_for_subject_section_year(subject_id, section_code, year_id, lecturer_id=lecturer_id)
    else:
        lectures_exist = bool(await db.list_lecture_titles_by_year(subject_id, section_code, year_id))
        cats = await db.list_categories_for_subject_section_year(subject_id, section_code, year_id)
    return await update.message.reply_text(
        "اختر نوع المحتوى:",
        reply_markup=generate_year_category_menu_keyboard(cats, lectures_exist),
    )
