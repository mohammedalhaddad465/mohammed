from ..helpers import nav_back_one

async def handle_smart_back(update, context):
    from ..main import render_state
    nav = context.user_data.get("nav", {})
    stack = nav.get("stack", [])
    if stack:
        top = stack[-1][0]
        if top == "year_category_menu":
            nav_back_one(context.user_data)
            nav_back_one(context.user_data)
            return await render_state(update, context)
        if top == "lecture_category_menu":
            nav_back_one(context.user_data)
            nav_back_one(context.user_data)
            return await render_state(update, context)
    nav_back_one(context.user_data)
    return await render_state(update, context)
