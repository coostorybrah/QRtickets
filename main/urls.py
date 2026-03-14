from django.urls import path
from . import views

urlpatterns = [
    # MAIN PATHS
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("chitietsukien/<str:event_id>/", views.event_detail, name="event_detail"),
    path("chitietsukien/<str:event_id>/buy-tickets/", views.buy_ticket, name="buy_ticket"),

    # USER PATHS
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('my-events/', views.my_events, name='my_events'),
    path('user/', views.user_page, name='user_page'),
    
    # API
    path("api/events/", views.api_events, name="api_events"),
    path("api/events/<str:event_id>/", views.api_event_detail, name="api_event_detail"),
    
    # AUTH PATHS
    path("api/login/", views.api_login),
    path("api/signup/", views.api_signup),
    path("api/me/", views.api_me),
    path("api/logout/", views.api_logout),

]