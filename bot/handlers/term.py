from ..helpers import nav_get_ids, nav_get_labels, get_db
from ..keyboards import generate_term_menu_keyboard_dynamic

async def render_term(update, context):
    level_id, term_id = nav_get_ids(context.user_data)
    level_label, term_label = nav_get_labels(context.user_data)
    db = get_db(context)
    flags = await db.term_feature_flags(level_id, term_id)
    return await update.message.reply_text(
        f"المستوى: {level_label}\nالترم: {term_label}\nاختر خيارًا:",
        reply_markup=generate_term_menu_keyboard_dynamic(flags),
    )
