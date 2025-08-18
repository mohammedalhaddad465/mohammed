from ..helpers import nav_get_ids, nav_set_subject, get_db
from ..keyboards import generate_subject_sections_keyboard_dynamic, generate_term_menu_keyboard_dynamic

async def handle_choose_subject(update, context, text):
    level_id, term_id = nav_get_ids(context.user_data)
    if not (level_id and term_id):
        return None
    db = get_db(context)
    subjects = await db.get_subjects_by_level_and_term(level_id, term_id)
    subject_names = {name for (name,) in subjects}
    if text in subject_names:
        subject_id = await db.get_subject_id_by_name(level_id, term_id, text)
        if subject_id is None:
            flags = await db.term_feature_flags(level_id, term_id)
            return await update.message.reply_text("تعذر العثور على المادة.", reply_markup=generate_term_menu_keyboard_dynamic(flags))
        nav_set_subject(context.user_data, text, subject_id)
        sections = await db.get_available_sections_for_subject(subject_id)
        return await update.message.reply_text(
            f"المادة: {text}\nاختر القسم:" if sections else "لا توجد أقسام متاحة لهذه المادة حتى الآن.",
            reply_markup=generate_subject_sections_keyboard_dynamic(sections),
        )
    return None
