from ..db import get_levels, get_terms_by_level
from ..helpers import nav_set_level, nav_push_view
from ..keyboards import generate_levels_keyboard, generate_terms_keyboard

async def handle_choose_level(update, context, text):
    levels = await get_levels()
    levels_map = {name: _id for _id, name in levels}
    if text in levels_map:
        level_id = levels_map[text]
        nav_set_level(context.user_data, text, level_id)
        terms = await get_terms_by_level(level_id)
        if not terms:
            return await update.message.reply_text("لا توجد أترام لهذا المستوى حتى الآن.", reply_markup=generate_levels_keyboard(levels))
        nav_push_view(context.user_data, "term_list")
        return await update.message.reply_text("اختر الترم:", reply_markup=generate_terms_keyboard(terms))
    return None
