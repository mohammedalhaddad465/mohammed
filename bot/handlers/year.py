from ..db import list_lecture_titles_by_year
from ..keyboards import generate_lecture_titles_keyboard

async def render_year(update, context):
    nav = context.user_data.get("nav", {})
    subject_id = nav.get("data", {}).get("subject_id")
    section_code = nav.get("data", {}).get("section")
    year_label = nav.get("stack", [])[-1][1] if nav.get("stack") else ""
    year_id = nav.get("data", {}).get("year_id")
    titles = await list_lecture_titles_by_year(subject_id, section_code, year_id)
    msg = f"السنة: {year_label}\nاختر محاضرة:" if titles else "لا توجد محاضرات لهذه السنة."
    return await update.message.reply_text(msg, reply_markup=generate_lecture_titles_keyboard(titles))
