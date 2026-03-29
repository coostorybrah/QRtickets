from payments.services.providers import paypal


def create_payment(order, provider="paypal"):
    if provider == "paypal":
        return paypal.create_order(order)

    raise ValueError("Unsupported payment provider")

def capture_payment(order, provider="paypal"):
    if provider == "paypal":
        return paypal.capture_order(order.payment_id)

    raise ValueError("Unsupported provider")