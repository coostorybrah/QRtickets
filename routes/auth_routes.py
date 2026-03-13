from flask import Blueprint, request, jsonify, session, redirect, url_for
from services.auth_service import login_user, signup_user, get_user_by_id

auth = Blueprint("auth", __name__)


@auth.route("/api/login", methods=["POST"])
def api_login():

    data = request.json

    result = login_user(
        data.get("username"),
        data.get("password")
    )

    if not result["success"]:
        return jsonify(result)

    user = result["user"]

    session["user"] = user["id"]

    return jsonify({
        "success": True,
        "username": user["username"],
        "avatar": user["avatar"]
    })


@auth.route("/api/signup", methods=["POST"])
def api_signup():

    data = request.json

    result = signup_user(
        data.get("username"),
        data.get("email"),
        data.get("password"),
        data.get("password_confirm")
    )

    if not result["success"]:
        return jsonify(result)

    user = result["user"]

    session["user"] = user["id"]

    return jsonify({
        "success": True,
        "username": user["username"],
        "avatar": user["avatar"],
        "message": "Đăng ký thành công!"
    })


@auth.route("/api/me")
def api_me():

    user_id = session.get("user")

    if not user_id:
        return jsonify({"loggedIn": False})

    user = get_user_by_id(user_id)

    if not user:
        return jsonify({"loggedIn": False})

    return jsonify({
        "loggedIn": True,
        "username": user["username"],
        "avatar": user["avatar"]
    })


@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main.trangchu"))