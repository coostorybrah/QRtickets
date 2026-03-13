from flask import Flask, session
from datetime import timedelta
from data_manager import load_user_db

from routes.main_routes import main
from routes.api_routes import api
from routes.auth_routes import auth

app = Flask(__name__)
app.secret_key = "fuckoff"
app.permanent_session_lifetime = timedelta(hours=1)

# Register blueprints
app.register_blueprint(main)
app.register_blueprint(api)
app.register_blueprint(auth)


# Allow templates to access current user
@app.context_processor
def inject_user():
    user_id = session.get("user")
    if not user_id:
        return dict(currentUser=None)

    users_db = load_user_db()

    user = next((u for u in users_db["users"] if u["id"] == user_id), None)

    return dict(currentUser=user)

# Refresh session timer on each request
@app.before_request
def refresh_session():
    if "user" in session:
        session.permanent = True
        session.modified = True


if __name__ == "__main__":
    app.run(debug=True)