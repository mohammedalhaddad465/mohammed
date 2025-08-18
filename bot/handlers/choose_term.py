from ..helpers import nav_get_ids, nav_set_term, get_db
from ..keyboards import generate_terms_keyboard, generate_term_menu_keyboard_dynamic

async def handle_choose_term(update, context, text):
    level_id, _ = nav_get_ids(context.user_data)
    if not level_id:
        return None
    db = get_db(context)
    terms = await db.get_terms_by_level(level_id)
    terms_map = {name: _id for _id, name in terms}
    if text in terms_map:
        term_id = terms_map[text]
        nav_set_term(context.user_data, text, term_id)
        flags = await db.term_feature_flags(level_id, term_id)
        return await update.message.reply_text("اختر:", reply_markup=generate_term_menu_keyboard_dynamic(flags))
    return None
