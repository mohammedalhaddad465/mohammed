from ..helpers import nav_back_to_levels
from ..keyboards import main_menu

async def handle_back_main_menu(update, context):
    nav_back_to_levels(context.user_data)
    return await update.message.reply_text("تم الرجوع إلى القائمة الرئيسية ⬇️", reply_markup=main_menu)
