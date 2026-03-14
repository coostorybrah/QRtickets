from django.shortcuts import render
from django.http import JsonResponse

from .services.events_service import search_events
from . import data_manager as dm

import json
import uuid

def home(request):
    return render(request, "trangchu.html")

# DATA TOAN BO SU KIEN
def api_events(request):
    events = dm.load_events_db()

    return JsonResponse(events, safe=False)

# DATA CHI TIET SU KIEN
def api_event_detail(request, event_id):
    events = dm.load_events_db()

    event = events.get(event_id)
    
    if not event:
        return JsonResponse({"error": "Event not found"}, status=404)
        
    return JsonResponse(event, safe=False)

# SEARCH
def search(request):
    query = request.GET.get("query", "").lower()
    location = request.GET.get("location", "")
    date = request.GET.get("date", "")
    categories = request.GET.getlist("category")

    price_min = int(request.GET.get("priceMin", 0))

    price_max = request.GET.get("priceMax")
    if price_max:
        price_max = int(price_max)
    else:
        price_max = None

    events_db = dm.load_events_db()

    results = search_events(
        events_db=events_db,
        query=query,
        location=location,
        categories=categories,
        date=date,
        price_min=price_min,
        price_max=price_max
    )

    context = {
        "query": query,
        "locations": [],
        "categories": dm.load_categories_db(),
        "selected_categories": categories,
        "location": location,
        "date": date,
        "price_ceiling": max(item["giaMax"] for item in events_db.values()),
        "priceMin": price_min,
        "priceMax": price_max,
        "search_results": json.dumps(results)
    }

    return render(request, "search.html", context)

# PAGE CHI TIET SU KIEN
def event_detail(request, event_id):
    return render(request, "chitietsukien.html", {"event_id": event_id})

# MUA VE
def buy_ticket(request, event_id):

    if request.method == "POST":

        ticket_type = request.POST.get("ticket_type")
        price = request.POST.get("price")

        tickets_db = dm.load_tickets_db()

        new_ticket = {
            "ticket_id": str(uuid.uuid4()),
            "event_id": event_id,
            "ticket_type": ticket_type,
            "price": int(price)
        }

        tickets_db["tickets"].append(new_ticket)

        dm.save_tickets_db(tickets_db)

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"})

# MY TICKETS PAGE 
def my_tickets(request):
    return render(request, "vecuatoi.html")


# USER PAGE
def user_page(request):
    return render(request, "userpage.html")


# MY EVENTS PAGE (CẤM XÓA)
def my_events(request):
    return render(request, "sukiencuatoi.html")

# ĐĂNG NHẬP
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    username = data.get("username")
    password = data.get("password")

    users = dm.load_user_db()

    for u in users["users"]:
        if u["username"] == username and u["password"] == password:

            request.session["user_id"] = u["id"]

            return JsonResponse({
                "success": True,
                "avatar": u["avatar"],
                "username": u["username"]
            })

    return JsonResponse({"error": "Invalid credentials"}, status=401)

# ĐĂNG KÝ
def api_signup(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    users = dm.load_user_db()

    new_user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": password,
        "email": email,
        "avatar": "/static/images/avatars/default-avatar.png",
        "role": "user"
    }

    users["users"].append(new_user)

    dm.save_user_db(users)

    request.session["user_id"] = new_user["id"]

    return JsonResponse({
        "success": True,
        "avatar": new_user["avatar"],
        "username": new_user["username"]
    })

# KIỂM TRA NẾU NGƯỜI DÙNG ĐÃ ĐĂNG NHẬP
def api_me(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "loggedIn": False
        })

    users = dm.load_user_db()

    for user in users["users"]:
        if user["id"] == user_id:
            return JsonResponse({
                "loggedIn": True,
                "avatar": user["avatar"],
                "username": user["username"]
            })

    return JsonResponse({
        "loggedIn": False
    })

# ĐĂNG XUẤT
def api_logout(request):

    request.session.pop("user_id", None)

    return JsonResponse({"success": True})