from django.shortcuts import render, redirect
from .form import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.is_active = True
            user.save()
            messages.success(request, 'Đăng ký thành công. Bạn có thể đăng nhập ngay bây giờ.')
            return redirect('login')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Bạn đã đăng nhập thành công.')
            return redirect('home')
        else:
            messages.error(request, 'Sai thông tin đăng nhập. Vui lòng kiểm tra lại.')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    # clear existing messages first so logout only shows one message
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    auth.logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công.')
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    from orders.models import Order
    orders = Order.objects.filter(
        user=request.user, is_ordered=True
    ).prefetch_related('items__product').order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/dashboard.html', context)
