from django.urls import path
from . import views

urlpatterns = [
    path("verify/", views.api_verify_payment),
]