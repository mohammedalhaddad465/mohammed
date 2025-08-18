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
# --- Handlers ---
from .handlers import (
    render_level,
    render_term_list,
    render_term,
    render_subject,
    render_subject_list,
    render_section,
    render_year,
    render_lecturer,
    render_year_list,
    render_lecturer_list,
    render_lecture_list,
    render_year_category_menu,
    render_lecture_category_menu,
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
    await update.message.reply_text(
        "👋 مرحبًا بك في بوت أرشيف قسم الميكاترونكس.\nاختر من القائمة:",
        reply_markup=main_menu)







# --------------------------------------------------------------------------
STATE_RENDERERS = {
    "level": render_level,
    "term_list": render_term_list,
    "term": render_term,
    "subject": render_subject,
    "subject_list": render_subject_list,
    "section": render_section,
    "year": render_year,
    "lecturer": render_lecturer,
    "year_list": render_year_list,
    "lecturer_list": render_lecturer_list,
    "lecture_list": render_lecture_list,
    "year_category_menu": render_year_category_menu,
    "lecture_category_menu": render_lecture_category_menu,
}

async def render_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nav = context.user_data.get("nav", {"stack": []})
    stack = nav.get("stack", [])

    if not stack:
        return await update.message.reply_text("اختر من القائمة:", reply_markup=main_menu)

    top_type = stack[-1][0]
    handler = STATE_RENDERERS.get(top_type)
    if handler:
        return await handler(update, context)

    return await update.message.reply_text("اختر من القائمة:", reply_markup=main_menu)

# --------------------------------------------------------------------------
async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message else ""

    handler = {
        BACK_TO_LEVELS: handle_back_to_levels,
        BACK_TO_SUBJECTS: handle_back_to_subjects,
        "📚 المستويات": handle_levels_menu,
        "🔙 العودة للقائمة الرئيسية": handle_back_main_menu,
        "🔙 العودة": handle_smart_back,
    }.get(text)

    if handler:
        return await handler(update, context)

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
            return result

    if text.startswith("/"):
        return await update.message.reply_text("هذا أمر خاص. لم يتم تفعيله بعد.")

    return await update.message.reply_text("الخيار غير معروف. ابدأ بـ: 📚 المستويات")









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
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))
   
    print("✅ Bot is running...")
    app.run_polling()























if __name__ == "__main__":
    try:
        main()
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")




