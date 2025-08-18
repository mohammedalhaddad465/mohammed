from ..helpers import nav_go_subject_list, nav_go_levels_list, nav_get_ids

async def handle_back_to_subjects(update, context):
    from ..main import render_state
    level_id, term_id = nav_get_ids(context.user_data)
    if level_id and term_id:
        nav_go_subject_list(context.user_data)
        return await render_state(update, context)
    nav_go_levels_list(context.user_data)
    return await render_state(update, context)
