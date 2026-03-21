from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from events.models import Event, Venue, Category

import json

# HOMEPAGE
def home(request):
    return render(request, "trangchu.html")

# PAGE CHI TIET SU KIEN
def event_detail(request, event_id):
    return render(request, "chitietsukien.html", {"event_id": event_id})

# MY TICKETS PAGE 
@login_required("/")
def my_tickets(request):
    return render(request, "vecuatoi.html")


# USER PAGE
@login_required("/")
def user_page(request):
    return render(request, "userpage.html")


# MY EVENTS PAGE (CẤM XÓA)
@login_required("/")
def my_events(request):
    return render(request, "sukiencuatoi.html")

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

    events = Event.objects.all()

    # FILTER
    if query:
        events = events.filter(name__icontains=query)

    if location:
        events = events.filter(venue__city__icontains=location)

    if date:
        events = events.filter(date=date)

    if categories:
        events = events.filter(categories__slug__in=categories).distinct()

    filtered_events = []
    for event in events:
        min_price = event.min_price or 0
        max_price_event = event.max_price or 0

        if price_min and max_price_event < price_min:
            continue

        if price_max and min_price > price_max:
            continue

        filtered_events.append(event)

    # FILTER RESULTS
    results = {}
    for event in filtered_events:
        results[event.slug] = {
            "ten": event.name,
            "anh": event.image,
            "giaMin": float(event.min_price) if event.min_price else 0,
            "displayDate": event.date.strftime("%d.%m.%Y"),
            "startTime": event.start_time.strftime("%H:%M") if event.start_time else "",
            "endTime": event.end_time.strftime("%H:%M") if event.end_time else "",
            "categories": [c.slug for c in event.categories.all()]
        }

    # FRONTEND
    output = {
        "query": query,
        "locations": Venue.objects.values_list("city", flat=True).distinct(),
        "categories": Category.objects.all(),
        "selected_categories": categories,
        "location": location,
        "date": date,
        "price_ceiling": max(
            (e.max_price or 0 for e in Event.objects.all()),
            default=0
        ),
        "priceMin": price_min,
        "priceMax": price_max,
        "search_results": json.dumps(results)
    }

    return render(request, "search.html", output)