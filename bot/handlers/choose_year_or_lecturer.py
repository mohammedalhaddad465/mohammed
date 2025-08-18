from ..keyboards import (
    generate_year_category_menu_keyboard,
    generate_lecturer_filter_keyboard,
)
from ..helpers import nav_set_year, nav_set_lecturer, nav_push_view, get_db

async def handle_choose_year_or_lecturer(update, context, text):
    db = get_db(context)
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    lecturer_id = nav.get("data", {}).get("lecturer_id")

    if not (subject_id and section_code):
        return None

    if lecturer_id:
        years = await db.get_years_for_subject_section_lecturer(subject_id, section_code, lecturer_id)
        years_map = {name: _id for _id, name in years}
        if text in years_map:
            year_id = years_map[text]
            nav_set_year(context.user_data, text, year_id)
            titles = await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id)
            lectures_exist = bool(titles)
            cats = await db.list_categories_for_subject_section_year(subject_id, section_code, year_id, lecturer_id=lecturer_id)
            nav_push_view(context.user_data, "year_category_menu")
            lecturer_label = next((lbl for t, lbl in nav.get('stack', []) if t=='lecturer'), '')
            return await update.message.reply_text(
                f"المحاضر: {lecturer_label}\nالسنة: {text}\nاختر نوع المحتوى:",
                reply_markup=generate_year_category_menu_keyboard(cats, lectures_exist),
            )
    else:
        years = await db.get_years_for_subject_section(subject_id, section_code)
        years_map = {name: _id for _id, name in years}
        if text in years_map:
            year_id = years_map[text]
            nav_set_year(context.user_data, text, year_id)
            titles = await db.list_lecture_titles_by_year(subject_id, section_code, year_id)
            lectures_exist = bool(titles)
            cats = await db.list_categories_for_subject_section_year(subject_id, section_code, year_id)
            nav_push_view(context.user_data, "year_category_menu")
            return await update.message.reply_text(
                f"السنة: {text}\nاختر نوع المحتوى:",
                reply_markup=generate_year_category_menu_keyboard(cats, lectures_exist),
            )

    lecturers = await db.get_lecturers_for_subject_section(subject_id, section_code)
    lect_map = {lec.name: lec.id for lec in lecturers}
    if text in lect_map:
        lecturer_id = lect_map[text]
        nav_set_lecturer(context.user_data, text, lecturer_id)
        years = await db.get_years_for_subject_section_lecturer(subject_id, section_code, lecturer_id)
        lectures_exist = await db.list_lecture_titles_by_lecturer(subject_id, section_code, lecturer_id)
        return await update.message.reply_text(
            f"المحاضر: {text}\nاختر خيارًا:",
            reply_markup=generate_lecturer_filter_keyboard(bool(years), bool(lectures_exist)),
        )
    return None
