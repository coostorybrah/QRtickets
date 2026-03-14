from ..data_manager import load_events_db


def get_all_events():
    return load_events_db()


def get_event(event_id):
    return load_events_db().get(event_id)


def search_events(
    events_db = None,
    query = "",
    location = "",
    categories = [],
    date = "",
    price_min = 0,
    price_max = None):

    events = events_db if (events_db is not None) else (load_events_db())
    if price_max is None:
        price_max = max(item["giaMax"] for item in events.values())

    results = {}

    for event_id, item in events.items():

        city = item["dcCuThe"].split(",")[-1].strip()

        if query and query not in item["ten"].lower():
            continue

        if location and location != city:
            continue

        if categories and not all(c in item["categories"] for c in categories):
            continue

        if date and date != item["date"]:
            continue

        if price_min and item["giaMax"] < price_min:
            continue

        if price_max and item["giaMin"] > price_max:
            continue

        results[event_id] = item

    return results