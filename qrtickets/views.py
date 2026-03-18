from django.shortcuts import render
from store.models import Product
from category.models import Category

# Create your views here

def home(request):
    categories = Category.objects.all()
    sections = []
    for category in categories:
        products = Product.objects.filter(category=category, is_available=True).order_by('-created_date')[:4]
        if products.exists():
            sections.append({'category': category, 'products': products})

    context = {
        'sections': sections,
    }
    return render(request, 'home.html', context)