from main.data_manager import load_user_db, save_user_db


def login_user(username, password):

    user = get_user_by_username(username)

    if not user:
        return {"success": False, "message": "Tài khoản không tồn tại."}

    if user["password"] != password:
        return {"success": False, "message": "Sai mật khẩu."}

    return {
        "success": True,
        "user": user
    }


def signup_user(username, email, password, password_confirm):

    users_db = load_user_db()

    if get_user_by_username(username, users_db):
        return {"success": False, "message": "Tài khoản đã tồn tại."}

    if get_user_by_email(email, users_db):
        return {"success": False, "message": "Email đã được sử dụng."}

    if password != password_confirm:
        return {"success": False, "message": "Mật khẩu không trùng khớp."}

    new_id = max((u["id"] for u in users_db["users"]), default=0) + 1

    new_user = {
        "id": new_id,
        "username": username,
        "password": password,
        "email": email,
        "avatar": "/static/images/avatars/default-avatar.png",
        "tickets": [],
        "events": []
    }

    users_db["users"].append(new_user)

    save_user_db(users_db)

    return {
        "success": True,
        "user": new_user
    }


def get_user_by_id(user_id, users_db = None):

    if (users_db is None):
        users_db = load_user_db()
        
    user_id = user_id.strip()

    return next((u for u in users_db["users"] if u["id"] == user_id), None)

def get_user_by_username(username, users_db = None):
    
    if (users_db is None):
        users_db = load_user_db()

    username = username.strip().lower()

    return next((u for u in users_db["users"] if u["username"].lower() == username), None)

def get_user_by_email(email, users_db = None):

    if (users_db is None):
        users_db = load_user_db()

    email = email.strip().lower()

    return next((u for u in users_db["users"] if u["email"].lower() == email), None)