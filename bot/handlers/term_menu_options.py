from ..helpers import nav_get_ids, nav_push_view, get_db
from ..keyboards import (
    generate_subjects_keyboard,
    generate_term_menu_keyboard_dynamic,
    main_menu,
    TERM_MENU_SHOW_SUBJECTS,
    TERM_MENU_PLAN,
    TERM_MENU_LINKS,
    TERM_MENU_ADV_SEARCH,
)

async def handle_term_menu_options(update, context, text):
    if text not in (TERM_MENU_SHOW_SUBJECTS, TERM_MENU_PLAN, TERM_MENU_LINKS, TERM_MENU_ADV_SEARCH):
        return None
    level_id, term_id = nav_get_ids(context.user_data)
    if not (level_id and term_id):
        return await update.message.reply_text("ابدأ باختيار المستوى ثم الترم.", reply_markup=main_menu)
    if text == TERM_MENU_SHOW_SUBJECTS:
        nav_push_view(context.user_data, "subject_list")
        db = get_db(context)
        subjects = await db.get_subjects_by_level_and_term(level_id, term_id)
        if not subjects:
            flags = await db.term_feature_flags(level_id, term_id)
            return await update.message.reply_text("لا توجد مواد لهذا الترم.", reply_markup=generate_term_menu_keyboard_dynamic(flags))
        return await update.message.reply_text("اختر المادة:", reply_markup=generate_subjects_keyboard(subjects))
    if text == TERM_MENU_PLAN:
        db = get_db(context)
        flags = await db.term_feature_flags(level_id, term_id)
        return await update.message.reply_text("الخطة الدراسية (قريبًا).", reply_markup=generate_term_menu_keyboard_dynamic(flags))
    if text == TERM_MENU_LINKS:
        db = get_db(context)
        flags = await db.term_feature_flags(level_id, term_id)
        return await update.message.reply_text("روابط المجموعات والقنوات (قريبًا).", reply_markup=generate_term_menu_keyboard_dynamic(flags))
    if text == TERM_MENU_ADV_SEARCH:
        db = get_db(context)
        flags = await db.term_feature_flags(level_id, term_id)
        return await update.message.reply_text("البحث المتقدم (قريبًا).", reply_markup=generate_term_menu_keyboard_dynamic(flags))
