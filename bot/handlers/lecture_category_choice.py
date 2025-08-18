from ..keyboards import generate_lecture_category_menu_keyboard, generate_lecture_titles_keyboard, LABEL_TO_CATEGORY
from ..helpers import nav_back_one, get_db

async def handle_lecture_category_choice(update, context, text):
    if text not in LABEL_TO_CATEGORY:
        return None
    nav = context.user_data.get("nav", {})
    stack = nav.get("stack", [])
    current = stack[-1][0] if stack else None
    if current != "lecture_category_menu":
        return None
    subject_id    = nav.get("data", {}).get("subject_id")
    section_code  = nav.get("data", {}).get("section")
    year_id       = nav.get("data", {}).get("year_id")
    lecturer_id   = nav.get("data", {}).get("lecturer_id")
    lecture_title = nav.get("data", {}).get("lecture_title")
    category      = LABEL_TO_CATEGORY[text]
    db = get_db(context)
    if not lecture_title:
        titles = await db.list_lecture_titles(subject_id, section_code)
        return await update.message.reply_text("اختر محاضرة أولًا:", reply_markup=generate_lecture_titles_keyboard(titles))
    mats = await db.get_materials_by_category(
        subject_id, section_code, category,
        year_id=year_id, lecturer_id=lecturer_id, title=lecture_title
    )
    if not mats:
        cats = await db.list_categories_for_lecture(subject_id, section_code, lecture_title, year_id=year_id, lecturer_id=lecturer_id)
        return await update.message.reply_text("لا توجد ملفات لهذا النوع.", reply_markup=generate_lecture_category_menu_keyboard(cats))
    for _id, title, url in mats:
        await update.message.reply_text(f"📄 {title}\n{url or '(لا يوجد رابط)'}")
    cats = await db.list_categories_for_lecture(subject_id, section_code, lecture_title, year_id=year_id, lecturer_id=lecturer_id)
    return await update.message.reply_text("اختر نوعًا آخر:", reply_markup=generate_lecture_category_menu_keyboard(cats))
