
import requests
from django.conf import settings

from payments.utils import currency

# GET ACCESS TOKEN
def get_access_token():
    url = f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token"

    response = requests.post(
        url,
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )

    data = response.json()
    return data["access_token"]

# CREATE ORDER
def create_order(order):
    access_token = get_access_token()

    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    usd_total_price = currency.convert_vnd_to_usd(order.get_total_price())
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": str(order.id),
                "amount": {
                    "currency_code": "USD",
                    "value": f"{usd_total_price:.2f}",
                }
            }
        ],
        "application_context": {
            "return_url": f"https://{settings.BASE_URL}/payment-return/",
            "cancel_url": f"https://{settings.BASE_URL}/orders-failed/"
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    # store PayPal order ID
    paypal_id = data.get("id")
    order.payment_id = paypal_id
    order.payment_provider = "paypal"
    order.save()

    for link in data.get("links", []):
        if link["rel"] == "approve":
            return link["href"]

    return None

# CAPTURE
def capture_order(paypal_id):
    access_token = get_access_token()

    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{paypal_id}/capture"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, headers=headers)

    if response.status_code != 201:
        print("[PAYPAL ERROR]", response.text)
        return False

    data = response.json()

    # Optional: validate status
    if data.get("status") != "COMPLETED":
        print("[PAYPAL NOT COMPLETED]", data)
        return False

    return True

