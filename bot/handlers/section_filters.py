from ..db import (
    get_years_for_subject_section,
    get_lecturers_for_subject_section,
    list_lecture_titles,
)
from ..helpers import nav_push_view
from ..keyboards import (
    FILTER_BY_YEAR,
    FILTER_BY_LECTURER,
    LIST_LECTURES,
    generate_years_keyboard,
    generate_lecturers_keyboard,
    generate_lecture_titles_keyboard,
    generate_subject_sections_keyboard_dynamic,
    main_menu,
)

async def handle_section_filters(update, context, text):
    if text not in {FILTER_BY_YEAR, FILTER_BY_LECTURER, LIST_LECTURES}:
        return None
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    if not (subject_id and section_code):
        return await update.message.reply_text("ابدأ باختيار المادة ثم القسم.", reply_markup=main_menu)
    if text == FILTER_BY_YEAR:
        years = await get_years_for_subject_section(subject_id, section_code)
        if not years:
            return await update.message.reply_text("لا توجد سنوات لهذا القسم.", reply_markup=generate_subject_sections_keyboard_dynamic([]))
        nav_push_view(context.user_data, "year_list")
        return await update.message.reply_text("اختر السنة:", reply_markup=generate_years_keyboard(years))
    if text == FILTER_BY_LECTURER:
        lecturers = await get_lecturers_for_subject_section(subject_id, section_code)
        if not lecturers:
            return await update.message.reply_text("لا يوجد محاضرون مرتبطون بهذا القسم.", reply_markup=generate_subject_sections_keyboard_dynamic([]))
        nav_push_view(context.user_data, "lecturer_list")
        return await update.message.reply_text("اختر المحاضر:", reply_markup=generate_lecturers_keyboard(lecturers))
    if text == LIST_LECTURES:
        titles = await list_lecture_titles(subject_id, section_code)
        if not titles:
            return await update.message.reply_text("لا توجد محاضرات متاحة.", reply_markup=generate_subject_sections_keyboard_dynamic([]))
        nav_push_view(context.user_data, "lecture_list")
        return await update.message.reply_text("اختر محاضرة:", reply_markup=generate_lecture_titles_keyboard(titles))
