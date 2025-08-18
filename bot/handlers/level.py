from ..db import get_levels
from ..keyboards import generate_levels_keyboard

async def render_level(update, context):
    levels = await get_levels()
    return await update.message.reply_text("اختر المستوى:", reply_markup=generate_levels_keyboard(levels))
