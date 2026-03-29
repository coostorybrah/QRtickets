from django.urls import path
from orders.views import *

urlpatterns = [
    path("", api_create_order),
    path("<int:order_id>/items/", api_add_items),
    path("<int:order_id>/status/", api_order_status),
    path("<int:order_id>/pay/", api_pay_order),
    path("<int:order_id>/cancel/", api_cancel_order),

    path("my-tickets/", api_my_tickets),
    path("check-in/", api_check_in_ticket),
]