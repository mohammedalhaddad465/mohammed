from ..keyboards import generate_lecture_titles_keyboard, generate_lecture_category_menu_keyboard
from ..helpers import nav_set_lecture, nav_push_view, nav_back_one, get_db

async def handle_lecture_title_choice(update, context, text):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    if not (subject_id and section_code):
        return None
    year_id = nav.get("data", {}).get("year_id")
    lecturer_id = nav.get("data", {}).get("lecturer_id")
    db = get_db(context)
    candidate_titles = set(await db.list_lecture_titles(subject_id, section_code))
    if year_id:
        candidate_titles.update(await db.list_lecture_titles_by_year(subject_id, section_code, year_id))
    if lecturer_id:
        candidate_titles.update(await db.list_lecture_titles_by_lecturer(subject_id, section_code, lecturer_id))
    if year_id and lecturer_id:
        candidate_titles.update(await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id))
    if text not in candidate_titles:
        return None
    nav_set_lecture(context.user_data, text)
    nav_push_view(context.user_data, "lecture_category_menu")
    cats = await db.list_categories_for_lecture(subject_id, section_code, text, year_id=year_id, lecturer_id=lecturer_id)
    if not cats:
        mats = await db.get_lecture_materials(subject_id, section_code, year_id=year_id, lecturer_id=lecturer_id, title=text)
        if mats:
            for _id, title, url in mats:
                await update.message.reply_text(f"📄 {title}\n{url or '(لا يوجد رابط)'}")
            titles = await db.list_lecture_titles(subject_id, section_code)
            if year_id and lecturer_id:
                titles = await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id)
            elif year_id:
                titles = await db.list_lecture_titles_by_year(subject_id, section_code, year_id)
            elif lecturer_id:
                titles = await db.list_lecture_titles_by_lecturer(subject_id, section_code, lecturer_id)
            nav_back_one(context.user_data)
            return await update.message.reply_text("اختر محاضرة أخرى:", reply_markup=generate_lecture_titles_keyboard(titles))
        nav_back_one(context.user_data)
        titles = await db.list_lecture_titles(subject_id, section_code)
        if year_id and lecturer_id:
            titles = await db.list_lecture_titles_by_lecturer_year(subject_id, section_code, lecturer_id, year_id)
        elif year_id:
            titles = await db.list_lecture_titles_by_year(subject_id, section_code, year_id)
        elif lecturer_id:
            titles = await db.list_lecture_titles_by_lecturer(subject_id, section_code, lecturer_id)
        return await update.message.reply_text("لا توجد أنواع ملفات لهذه المحاضرة.", reply_markup=generate_lecture_titles_keyboard(titles))
    return await update.message.reply_text(
        f"المحاضرة: {text}\nاختر نوع الملف:",
        reply_markup=generate_lecture_category_menu_keyboard(cats),
    )
