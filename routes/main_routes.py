from flask import Blueprint, render_template, request
from data_manager import load_events_db
from services.events_service import search_events

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/trangchu")
def trangchu():
    return render_template("trangchu.html")


@main.route("/chitietsukien/<string:event_id>", methods=["GET", "POST"])
def chitietsukien(event_id):
    return render_template("chitietsukien.html", event_id=event_id)


@main.route("/search")
def search():

    query = request.args.get("query", "").lower()
    location = request.args.get("location", "")
    selected_categories = request.args.getlist("category")
    date = request.args.get("date", "")
    input_price_min = request.args.get("priceMin", type=int)
    input_price_max = request.args.get("priceMax", type=int)

    events_backend_data = load_events_db()

    price_ceiling = 0
    for item in events_backend_data.values():
        if item["giaMax"] > price_ceiling:
            price_ceiling = item["giaMax"]

    if input_price_min is None:
        input_price_min = 0

    if input_price_max is None:
        input_price_max = price_ceiling

    locations = set()
    categories = set()

    for item in events_backend_data.values():

        city = item["dcCuThe"].split(",")[-1].strip()
        locations.add(city)

        categories.update(item["categories"])

    search_results = search_events(
        events_backend_data,
        query,
        location,
        selected_categories,
        date,
        input_price_min,
        input_price_max
    )

    return render_template(
        "search.html",
        search_results=search_results,
        query=query,
        location=location,
        selected_categories=selected_categories,
        date=date,
        priceMin=input_price_min,
        price_ceiling=price_ceiling,
        priceMax=input_price_max,
        locations=sorted(locations),
        categories=sorted(categories)
    )


@main.route("/sukiencuatoi")
def sukiencuatoi():
    return render_template("sukiencuatoi.html")


@main.route("/vecuatoi")
def vecuatoi():
    return render_template("vecuatoi.html")


@main.route("/userpage")
def userpage():
    return render_template("userpage.html")