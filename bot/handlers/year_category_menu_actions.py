from ..keyboards import (
    generate_lecture_titles_keyboard,
    generate_year_category_menu_keyboard,
    LABEL_TO_CATEGORY,
    YEAR_MENU_LECTURES,
)
from ..helpers import nav_push_view, get_db

async def handle_year_category_menu_actions(update, context, text):
    if text != YEAR_MENU_LECTURES and text not in LABEL_TO_CATEGORY:
        return None
    nav = context.user_data.get("nav", {})
    stack = nav.get("stack", [])
    current = stack[-1][0] if stack else None
    if current != "year_category_menu":
        return None
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    year_id = nav.get("data", {}).get("year_id")
    lecturer_id = nav.get("data", {}).get("lecturer_id")
    db = get_db(context)
    if text == YEAR_MENU_LECTURES:
        if lecturer_id and year_id:
            titles = await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id)
        else:
            titles = await db.list_lecture_titles_by_year(subject_id, section_code, year_id)
        if not titles:
            cats = await db.list_categories_for_subject_section_year(subject_id, section_code, year_id, lecturer_id=lecturer_id)
            return await update.message.reply_text("لا توجد محاضرات لهذه السنة.", reply_markup=generate_year_category_menu_keyboard(cats, False))
        nav_push_view(context.user_data, "lecture_list")
        return await update.message.reply_text("اختر محاضرة:", reply_markup=generate_lecture_titles_keyboard(titles))
    if text in LABEL_TO_CATEGORY:
        category = LABEL_TO_CATEGORY[text]
        if category == "lecture":
            if lecturer_id and year_id:
                titles = await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id)
            else:
                titles = await db.list_lecture_titles_by_year(subject_id, section_code, year_id)
            nav_push_view(context.user_data, "lecture_list")
            return await update.message.reply_text("اختر محاضرة أولًا:", reply_markup=generate_lecture_titles_keyboard(titles))
        mats = await db.get_materials_by_category(
            subject_id, section_code, category,
            year_id=year_id, lecturer_id=lecturer_id
        )
        if not mats:
            titles_exist = False
            if lecturer_id and year_id:
                titles_exist = bool(await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id))
            else:
                titles_exist = bool(await db.list_lecture_titles_by_year(subject_id, section_code, year_id))
            cats = await db.list_categories_for_subject_section_year(subject_id, section_code, year_id, lecturer_id=lecturer_id)
            return await update.message.reply_text("لا توجد ملفات لهذا التصنيف.", reply_markup=generate_year_category_menu_keyboard(cats, titles_exist))
        for mat in mats:
            await update.message.reply_text(f"📄 {mat.title}\n{mat.url or '(لا يوجد رابط)'}")
        titles_exist = False
        if lecturer_id and year_id:
            titles_exist = bool(await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id))
        else:
            titles_exist = bool(await db.list_lecture_titles_by_year(subject_id, section_code, year_id))
        cats = await db.list_categories_for_subject_section_year(subject_id, section_code, year_id, lecturer_id=lecturer_id)
        return await update.message.reply_text("اختر نوع محتوى آخر:", reply_markup=generate_year_category_menu_keyboard(cats, titles_exist))
    return None
