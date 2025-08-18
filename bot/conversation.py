"""Conversation states and helpers."""

# حالة الحوار ممثلة بأرقام ثابتة مفهومة لـ ConversationHandler
# نستخدم أرقامًا بسيطة بدل Enum ليتوافق مباشرة مع متطلبات المكتبة.

LEVEL, TERM_LIST, TERM, SUBJECT_LIST, SECTION, YEAR, LECTURER, YEAR_LIST, LECTURER_LIST, LECTURE_LIST, YEAR_CATEGORY_MENU, LECTURE_CATEGORY_MENU = range(12)

# خريطة من نوع العقدة في نظام التنقل القديم إلى الحالة المكافئة في ConversationHandler
NODE_TO_STATE = {
    "level": LEVEL,
    "term_list": TERM_LIST,
    "term": TERM,
    "subject_list": SUBJECT_LIST,
    # بعد اختيار المادة أو القسم نعمل ضمن نفس الحالة لأنها مشتركة
    "subject": SECTION,
    "section": SECTION,
    "year": YEAR,
    "lecturer": LECTURER,
    "year_list": YEAR_LIST,
    "lecturer_list": LECTURER_LIST,
    "lecture_list": LECTURE_LIST,
    "year_category_menu": YEAR_CATEGORY_MENU,
    "lecture_category_menu": LECTURE_CATEGORY_MENU,
}

# قائمة بجميع الحالات لتعريفها داخل ConversationHandler
ALL_STATES = list(set(NODE_TO_STATE.values()))


def get_state(user_data: dict) -> int:
    """يستخرج الحالة الحالية من بيانات المستخدم بناءً على أعلى عنصر في المكدس."""
    nav = user_data.get("nav", {})
    stack = nav.get("stack", [])
    if not stack:
        # الحالة الافتراضية: اختيار المستوى
        return LEVEL
    top_type = stack[-1][0]
    return NODE_TO_STATE.get(top_type, LEVEL)
