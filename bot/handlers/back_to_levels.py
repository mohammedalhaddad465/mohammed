from ..helpers import nav_go_levels_list

async def handle_back_to_levels(update, context):
    from ..main import render_state
    nav_go_levels_list(context.user_data)
    return await render_state(update, context)
