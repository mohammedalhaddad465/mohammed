from ..keyboards import generate_lecture_category_menu_keyboard
from ..helpers import get_db

async def render_lecture_category_menu(update, context):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    year_id = nav.get("data", {}).get("year_id")
    lecturer_id = nav.get("data", {}).get("lecturer_id")
    lecture_title = nav.get("data", {}).get("lecture_title", "")
    db = get_db(context)
    cats = await db.list_categories_for_lecture(subject_id, section_code, lecture_title, year_id=year_id, lecturer_id=lecturer_id)
    msg = f"المحاضرة: {lecture_title}\nاختر نوع الملف:" if cats else "لا توجد أنواع ملفات لهذه المحاضرة."
    return await update.message.reply_text(msg, reply_markup=generate_lecture_category_menu_keyboard(cats))
