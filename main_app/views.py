from django.shortcuts import render, redirect, get_object_or_404
from .models import MenuItem, Order, OrderItem
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm,ContactForm
from django.contrib import messages

# Create your views here.



def home(request):
    return render(request, 'app/home.html')

@login_required
def menu(request):
    menu_items = MenuItem.objects.all()
    cart_item_count = 0
    if request.user.is_authenticated:
        current_order = Order.objects.filter(user=request.user, is_completed=False).first()
        if current_order:
            cart_item_count = current_order.cart_item_count()
    return render(request, 'app/our_menu.html', {'menu_items': menu_items, 'cart_item_count': cart_item_count})
@login_required
def create_order(request):
    order = Order.objects.create()

    return redirect('order_detail', order_id=order.id)
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    menu_items = MenuItem.objects.all()

    if request.method == "POST":
        menu_item_id = request.POST.get('menu_item_id')
        quantity = int(request.POST.get('quantity', 1))
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)

        
        order_item, created = OrderItem.objects.get_or_create(order=order, menu_item=menu_item)
        order_item.quantity += quantity
        order_item.save()

    items = order.items.all()  
    total_order_price = sum(item.total_price() for item in items)
    cart_item_count = order.cart_item_count()
    return render(request, 'app/order_detail.html', {
        'order': order,
        'items': items,
        'menu_items': menu_items,
        'cart_item_count': cart_item_count,
        
    })

def remove_order_item(request, order_id, item_id):
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, id=item_id, order=order)
    order_item.delete()
    return redirect('order_detail', order_id=order.id)

def about(request):
    return render(request, 'app/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the data to the database
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  # Replace 'contact' with your contact URL name
    else:
        form = ContactForm()
    return render(request, 'app/contact.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home') 
    else:
        form = CustomAuthenticationForm()
    return render(request, 'app/login.html', {'form': form})
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/register.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')  