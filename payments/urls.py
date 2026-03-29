from django.urls import path
from . import views

urlpatterns = [
    path("verify/", views.verify_payment),
    path("find-order/", views.find_order_by_paypal),
]