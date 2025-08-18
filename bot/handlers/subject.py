from ..db import get_available_sections_for_subject
from ..keyboards import generate_subject_sections_keyboard_dynamic

async def render_subject(update, context):
    nav = context.user_data.get("nav", {})
    subject_label = nav.get("stack", [])[-1][1] if nav.get("stack") else ""
    subject_id = nav.get("data", {}).get("subject_id")
    sections = await get_available_sections_for_subject(subject_id) if subject_id else []
    msg = f"المادة: {subject_label}\nاختر القسم:" if sections else "لا توجد أقسام متاحة لهذه المادة حتى الآن."
    return await update.message.reply_text(msg, reply_markup=generate_subject_sections_keyboard_dynamic(sections))
