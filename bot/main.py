# main.py
# نقطة الدخول للبوت (وضع Reply Keyboard)
# تنظير: لا تغييرات على الخوارزمية، فقط تنظيف الاستيرادات

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from .config import BOT_TOKEN

# --- DB: استيراد صريح للدوال المستخدمة فقط ---
from .db import init_db

# from reaction import handle_reaction

# --- Keyboards (Reply) ---
from .keyboards import (
    main_menu,
    BACK_TO_LEVELS,
    BACK_TO_SUBJECTS,
)
# --- Conversation states ---
from .conversation import ALL_STATES, get_state, LEVEL
from .helpers import nav_go_levels_list
# --- Handlers ---
from .handlers import (
    handle_back_to_levels,
    handle_back_to_subjects,
    handle_levels_menu,
    handle_back_main_menu,
    handle_smart_back,
    handle_choose_level,
    handle_choose_term,
    handle_term_menu_options,
    handle_choose_subject,
    handle_choose_section,
    handle_section_filters,
    handle_choose_year_or_lecturer,
    handle_lecturer_list_actions,
    handle_year_category_menu_actions,
    handle_lecture_title_choice,
    handle_lecture_category_choice,
)


# --------------------------------------------------------------------------
# إعداد التسجيل لرؤية الرسائل التفصيلية
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نقطة الدخول لبدء المحادثة."""
    nav_go_levels_list(context.user_data)
    await update.message.reply_text(
        "👋 مرحبًا بك في بوت أرشيف قسم الميكاترونكس.\nاختر من القائمة:",
        reply_markup=main_menu,
    )
    return LEVEL







# --------------------------------------------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل الأساسي ضمن ConversationHandler."""
    text = update.message.text if update.message else ""

    handler = {
        BACK_TO_LEVELS: handle_back_to_levels,
        BACK_TO_SUBJECTS: handle_back_to_subjects,
        "📚 المستويات": handle_levels_menu,
        "🔙 العودة للقائمة الرئيسية": handle_back_main_menu,
        "🔙 العودة": handle_smart_back,
    }.get(text)

    if handler:
        await handler(update, context)
        return get_state(context.user_data)

    dynamic_handlers = [
        handle_choose_level,
        handle_choose_term,
        handle_term_menu_options,
        handle_choose_subject,
        handle_choose_section,
        handle_section_filters,
        handle_choose_year_or_lecturer,
        handle_lecturer_list_actions,
        handle_year_category_menu_actions,
        handle_lecture_title_choice,
        handle_lecture_category_choice,
    ]

    for func in dynamic_handlers:
        result = await func(update, context, text)
        if result:
            return get_state(context.user_data)

    if text.startswith("/"):
        await update.message.reply_text("هذا أمر خاص. لم يتم تفعيله بعد.")
    else:
        await update.message.reply_text("الخيار غير معروف. ابدأ بـ: 📚 المستويات")

    return get_state(context.user_data)









# --------------------------------------------------------------------------
def main():
    # سياسة loop مناسبة لويندوز
    if os.name == "nt":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass

    # تأكد من وجود event loop للـ MainThread (مهم لبايثون 3.12)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # تهيئة قاعدة البيانات
    loop.run_until_complete(init_db())

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={state: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)] for state in ALL_STATES},
        fallbacks=[],
    )
    app.add_handler(conv_handler)
   
    print("✅ Bot is running...")
    app.run_polling()























if __name__ == "__main__":
    try:
        main()
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")




