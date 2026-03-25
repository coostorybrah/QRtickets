import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from carts.models import Cart, CartItem
from orders.models import Order, OrderItem
from store.models import Product, Variation

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def _get_or_create_cart(request):
    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
    return cart


def _clear_cart(cart):
    CartItem.objects.filter(cart=cart).delete()

@login_required(login_url='login')
def add_cart(request, product_id):

    product = Product.objects.get(id=product_id) #get the product
    product_variation = [] 
    variation_source = request.POST if request.method == 'POST' else request.GET
    for item in variation_source:
        if item in ['csrfmiddlewaretoken']:
            continue
        key = item
        value = variation_source.get(key)
        if not value:
            continue

        try:
            variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
            product_variation.append(variation) #store this values inside a cart item 
        except Variation.DoesNotExist:
            pass


    cart = _get_or_create_cart(request)

    existing_items = CartItem.objects.filter(cart=cart, is_active=True)
    other_items = existing_items.exclude(product=product)
    if other_items.exists():
        other_items.delete()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if len(product_variation) > 0:
            cart_item.variations.clear()
            for item in product_variation:
                cart_item.variations.add(item)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if len(product_variation) > 0:
            for item in product_variation:
                cart_item.variations.add(item)
    cart_item.save()
    return redirect('cart')


def checkout(request):
    total = 0
    quantity = 0
    cart_items = []
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.sub_total()
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
    }
    return render(request, 'store/checkout.html', context)


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart') 

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))# return a product
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)# return all item 
        for cart_item in cart_items:
            total += cart_item.sub_total()
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def clear_cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        _clear_cart(cart)
    except Cart.DoesNotExist:
        pass

    return JsonResponse({'status': 'cleared'})


@require_POST
def complete_order(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        body = {}

    paypal_order_id = body.get('order_id', '')

    try:
        with transaction.atomic():
            cart = Cart.objects.select_for_update().get(cart_id=_cart_id(request))
            cart_items = list(CartItem.objects.select_related('product').filter(cart=cart, is_active=True))

            if not cart_items:
                return JsonResponse({'status': 'error', 'message': 'Cart is empty.'}, status=400)

            total = sum(item.sub_total() for item in cart_items)

            for item in cart_items:
                product = Product.objects.select_for_update().get(id=item.product_id)
                if item.quantity > product.stock:
                    return JsonResponse(
                        {'status': 'error', 'message': f'{product.product_name} does not have enough tickets.'},
                        status=400,
                    )

                product.stock -= item.quantity
                if product.stock <= 0:
                    product.stock = 0
                    product.is_available = False
                product.save()

            if request.user.is_authenticated:
                order = Order.objects.create(
                    user=request.user,
                    order_number=paypal_order_id or _cart_id(request),
                    first_name=request.user.first_name,
                    last_name=request.user.last_name,
                    phone=getattr(request.user, 'phone_number', ''),
                    email=request.user.email,
                    order_total=total,
                    tax=0,
                    status='Completed',
                    ip=request.META.get('REMOTE_ADDR', ''),
                    is_ordered=True,
                )
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.unit_price(),
                    )

            _clear_cart(cart)

            if request.user.is_authenticated:
                try:
                    mail_subject = 'Xác nhận đặt vé thành công - QRtickets'
                    message = render_to_string('orders/order_recieved_email.html', {
                        'user': request.user,
                        'order': order,
                        'order_items': order.items.select_related('product').all(),
                    })
                    email = EmailMessage(mail_subject, message, to=[request.user.email])
                    email.send(fail_silently=True)
                except Exception:
                    pass

    except Cart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cart not found.'}, status=404)

    return JsonResponse({'status': 'ok', 'redirect_url': '/cart/order-success/'})


def order_success(request):
    return render(request, 'store/order_success.html')