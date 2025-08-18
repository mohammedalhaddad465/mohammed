from ..helpers import nav_get_ids
from ..db import get_subjects_by_level_and_term
from ..keyboards import generate_subjects_keyboard

async def render_subject_list(update, context):
    level_id, term_id = nav_get_ids(context.user_data)
    subjects = await get_subjects_by_level_and_term(level_id, term_id)
    msg = "اختر المادة:" if subjects else "لا توجد مواد لهذا الترم."
    return await update.message.reply_text(msg, reply_markup=generate_subjects_keyboard(subjects))
