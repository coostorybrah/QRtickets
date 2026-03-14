from . import data_manager as dm

def current_user(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return {"user": None}

    users = dm.load_user_db()

    for user in users["users"]:
        if user["id"] == user_id:
            return {"user": user}

    return {"user": None}