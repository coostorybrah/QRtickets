import json
import os
from django.conf import settings

BASE_DIR = settings.BASE_DIR

USER_DB_PATH = os.path.join(BASE_DIR, "data", "users.json")
EVENTS_DB_PATH = os.path.join(BASE_DIR, "data", "events.json")
CATEGORIES_DB_PATH = os.path.join(BASE_DIR, "data", "categories.json")
TICKETS_DB_PATH = os.path.join(BASE_DIR, "data", "tickets.json")

def load_user_db():
    with open(USER_DB_PATH, "r", encoding="utf-8") as user_file:
        return json.load(user_file)
    
def load_events_db():
    with open(EVENTS_DB_PATH, "r", encoding="utf-8") as events_file:
        return json.load(events_file)

def load_categories_db():
    with open(CATEGORIES_DB_PATH, "r", encoding="utf-8") as events_file:
        return json.load(events_file)
    
def save_user_db(data):
    with open(USER_DB_PATH, "w", encoding="utf-8") as user_file:
        json.dump(data, user_file, indent=4, ensure_ascii=False)
        
def find_user_by_username(username):
    users_db = load_user_db()
    for user in users_db["users"]:
        if user["username"] == username:
            return user
    return None

def find_user_by_email(email):
    users_db = load_user_db()
    for user in users_db["users"]:
        if user["email"] == email:
            return user
    return None

def load_tickets_db():
    with open(TICKETS_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tickets_db(data):
    with open(TICKETS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)