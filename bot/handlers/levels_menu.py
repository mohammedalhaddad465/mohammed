from ..helpers import nav_back_to_levels
from ..db import get_levels
from ..keyboards import generate_levels_keyboard

async def handle_levels_menu(update, context):
    nav_back_to_levels(context.user_data)
    levels = await get_levels()
    return await update.message.reply_text("اختر المستوى:", reply_markup=generate_levels_keyboard(levels))
