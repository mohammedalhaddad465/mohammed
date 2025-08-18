from ..helpers import nav_back_to_levels, get_db
from ..keyboards import generate_levels_keyboard

async def handle_levels_menu(update, context):
    nav_back_to_levels(context.user_data)
    db = get_db(context)
    levels = await db.get_levels()
    return await update.message.reply_text("اختر المستوى:", reply_markup=generate_levels_keyboard(levels))
