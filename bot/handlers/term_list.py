from ..helpers import nav_get_ids, nav_get_labels
from ..db import get_terms_by_level
from ..keyboards import generate_terms_keyboard

async def render_term_list(update, context):
    level_id, _ = nav_get_ids(context.user_data)
    level_label, _ = nav_get_labels(context.user_data)
    terms = await get_terms_by_level(level_id)
    return await update.message.reply_text(
        f"المستوى: {level_label}\nاختر الترم:",
        reply_markup=generate_terms_keyboard(terms),
    )
