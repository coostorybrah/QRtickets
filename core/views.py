from django.shortcuts import render

def home(request):
    return render(request, "trangchu.html")

def search(request):
    return render(request, "search.html")

def my_events(request):
    return render(request, "sukiencuatoi.html")

def my_tickets(request):
    return render(request, "vecuatoi.html")

def user_page(request):
    return render(request, "userpage.html")