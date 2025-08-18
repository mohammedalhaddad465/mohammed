from ..helpers import nav_push_view
from ..db import (
    get_years_for_subject_section_lecturer,
    list_lecture_titles_by_lecturer,
)
from ..keyboards import (
    generate_years_keyboard,
    generate_lecturer_filter_keyboard,
    generate_lecture_titles_keyboard,
    main_menu,
    CHOOSE_YEAR_FOR_LECTURER,
    LIST_LECTURES_FOR_LECTURER,
)

async def handle_lecturer_list_actions(update, context, text):
    if text not in {CHOOSE_YEAR_FOR_LECTURER, LIST_LECTURES_FOR_LECTURER}:
        return None
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    lecturer_id = nav.get("data", {}).get("lecturer_id")
    lecturer_label = next((lbl for t, lbl in nav.get("stack", []) if t == "lecturer"), "")
    if not (subject_id and section_code and lecturer_id):
        return await update.message.reply_text("ابدأ باختيار المادة → القسم → المحاضر.", reply_markup=main_menu)
    if text == CHOOSE_YEAR_FOR_LECTURER:
        years = await get_years_for_subject_section_lecturer(subject_id, section_code, lecturer_id)
        if not years:
            years_exist = False
            lectures_exist = await list_lecture_titles_by_lecturer(subject_id, section_code, lecturer_id)
            return await update.message.reply_text(
                "لا توجد سنوات مرتبطة بمحاضرات هذا المحاضر.",
                reply_markup=generate_lecturer_filter_keyboard(years_exist, bool(lectures_exist)),
            )
        nav_push_view(context.user_data, "year_list")
        return await update.message.reply_text(
            f"المحاضر: {lecturer_label}\nاختر السنة:",
            reply_markup=generate_years_keyboard(years),
        )
    if text == LIST_LECTURES_FOR_LECTURER:
        titles = await list_lecture_titles_by_lecturer(subject_id, section_code, lecturer_id)
        if not titles:
            years = await get_years_for_subject_section_lecturer(subject_id, section_code, lecturer_id)
            return await update.message.reply_text(
                "لا توجد محاضرات لهذا المحاضر.",
                reply_markup=generate_lecturer_filter_keyboard(bool(years), False),
            )
        nav_push_view(context.user_data, "lecture_list")
        return await update.message.reply_text(
            f"المحاضر: {lecturer_label}\nاختر محاضرة:",
            reply_markup=generate_lecture_titles_keyboard(titles),
        )
