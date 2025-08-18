from ..keyboards import generate_levels_keyboard
from ..helpers import get_db

async def render_level(update, context):
    db = get_db(context)
    levels = await db.get_levels()
    return await update.message.reply_text("اختر المستوى:", reply_markup=generate_levels_keyboard(levels))
