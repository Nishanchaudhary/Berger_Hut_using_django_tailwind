import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from .models import *
from .forms import *
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse

# Set up logging
logger = logging.getLogger(__name__)

def about(request):
    logger.debug("About page accessed")
    return render(request, 'app/about.html')

def contact(request):
    logger.debug("Contact page accessed")
    return render(request, 'app/contact.html')

# Profile Management
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            profile, created = CustomUser.objects.get_or_create(user=request.user)
            logger.info(f"Profile {'created' if created else 'retrieved'} for user {request.user.username}")
            form = ProfileForm(instance=profile)
            return render(request, 'app/profile.html', {'form': form})
        except Exception as e:
            logger.error(f"Error accessing profile for user {request.user.username}: {str(e)}")
            messages.error(request, "An error occurred while accessing your profile.")
            return redirect('home')
    
    def post(self, request):
        try:
            profile = get_object_or_404(CustomUser, user=request.user)
            form = ProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                logger.info(f"Profile updated successfully for user {request.user.username}")
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                logger.warning(f"Profile form validation failed for user {request.user.username}")
                return render(request, 'app/profile.html', {'form': form})
        except Exception as e:
            logger.error(f"Error updating profile for user {request.user.username}: {str(e)}")
            messages.error(request, "An error occurred while updating your profile.")
            return redirect('profile')

# Main Views
class HomeView(View):
    def get(self, request):
        try:
            cart_count = 0
            if request.user.is_authenticated:
                pending_order = Order.objects.filter(
                    user=request.user,
                    status='pending'
                ).prefetch_related('items').first()
                cart_count = pending_order.items.count() if pending_order else 0
                logger.debug(f"Cart count for user {request.user.username}: {cart_count}")

            context = {
                'categories': Category.objects.filter(is_active=True).order_by('display_order'),
                'featured_items': MenuItem.objects.filter(is_available=True).order_by('?')[:8],
                'promotions': Promotion.get_active_promotions(),
                'cart_count': cart_count,
            }
            logger.debug("Home page loaded successfully")
            return render(request, 'app/home.html', context)
        except Exception as e:
            logger.error(f"Error loading home page: {str(e)}")
            messages.error(request, "An error occurred while loading the home page.")
            return render(request, 'app/home.html', {})

class MenuView(ListView):
    model = MenuItem
    template_name = 'app/menu_list.html'
    context_object_name = 'menu_items'
    paginate_by = 12
    
    def get_queryset(self):
        try:
            queryset = MenuItem.objects.filter(is_available=True)
            category_slug = self.kwargs.get('category_slug')
            if category_slug:
                logger.debug(f"Filtering menu by category: {category_slug}")
                queryset = queryset.filter(category__slug=category_slug)
            return queryset.order_by('category__display_order', 'name')
        except Exception as e:
            logger.error(f"Error retrieving menu items: {str(e)}")
            return MenuItem.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['categories'] = Category.objects.filter(is_active=True)
            context['current_category'] = self.kwargs.get('category_slug')
        except Exception as e:
            logger.error(f"Error getting menu context data: {str(e)}")
        return context

class MenuItemDetailView(DetailView):
    model = MenuItem
    template_name = 'app/menu_item_detail.html'
    context_object_name = 'item'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            item = self.object
            context['reviews'] = Review.objects.filter(menu_item=item).order_by('-created_at')
            context['review_form'] = ReviewForm()
            logger.debug(f"Loaded details for menu item: {item.name}")
        except Exception as e:
            logger.error(f"Error getting menu item detail context: {str(e)}")
        return context
    
    def post(self, request, *args, **kwargs):
        item = self.get_object()
        form = ReviewForm(request.POST)
    
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.user = request.user
                review.menu_item = item
                review.save()
                logger.info(f"New review added for {item.name} by {request.user.username}")
                messages.success(request, "Thank you for your review!")
            except IntegrityError:
                logger.warning(f"Duplicate review attempt by {request.user.username} for {item.name}")
                messages.error(request, "You've already reviewed this item")
            except Exception as e:
                logger.error(f"Error saving review: {str(e)}")
                messages.error(request, "An error occurred while saving your review.")
        
            return redirect('menu_item_detail', pk=item.pk)
    
        logger.warning(f"Invalid review form submission by {request.user.username}")
        return self.render_to_response(self.get_context_data(form=form))

# Cart and Order Views
class CartView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            order = Order.get_pending_order(request.user)
            logger.debug(f"Cart viewed by {request.user.username}, order ID: {order.id if order else 'None'}")
            context = {
                'order': order,
                'items': order.items.select_related('menu_item') if order else [],
                'promo_form': PromotionForm(),
                'delivery_charge': Decimal('2.00') 
            }
            return render(request, 'app/cart.html', context)
        except Exception as e:
            logger.error(f"Error viewing cart for {request.user.username}: {str(e)}")
            messages.error(request, "An error occurred while loading your cart.")
            return render(request, 'app/cart.html', {'order': None, 'items': []})

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        try:
            menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
            order = Order.get_pending_order(request.user)
            
            special_instructions = request.POST.get('special_instructions', '')
            
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                menu_item=menu_item,
                defaults={
                    'quantity': 1,
                    'special_requests': special_instructions
                }
            )
            
            if not created:
                order_item.quantity += 1
                if special_instructions:
                    order_item.special_requests = special_instructions
                order_item.save()
            
            logger.info(f"Item {menu_item.name} added to cart for {request.user.username}")
            messages.success(request, f"{menu_item.name} added to your cart")
        except Exception as e:
            logger.error(f"Error adding item {item_id} to cart for {request.user.username}: {str(e)}")
            messages.error(request, "An error occurred while adding the item to your cart.")
        
        return redirect(request.META.get('HTTP_REFERER', 'menu'))

class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        try:
            order_item = get_object_or_404(
                OrderItem, 
                id=item_id, 
                order__user=request.user,
                order__status='pending'
            )
            
            action = request.POST.get('action')
            
            if action == 'increase':
                order_item.quantity += 1
                order_item.save()
                logger.info(f"Increased quantity for order item {order_item.id} for {request.user.username}")
                messages.info(request, f"Quantity increased for {order_item.menu_item.name}")
            elif action == 'decrease':
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    logger.info(f"Decreased quantity for order item {order_item.id} for {request.user.username}")
                    messages.info(request, f"Quantity decreased for {order_item.menu_item.name}")
                else:
                    order_item.delete()
                    logger.info(f"Removed item {order_item.menu_item.name} from cart for {request.user.username}")
                    messages.info(request, f"{order_item.menu_item.name} removed from cart")
                    return redirect('cart')
            elif action == 'remove':
                order_item.delete()
                logger.info(f"Removed item {order_item.menu_item.name} from cart for {request.user.username}")
                messages.info(request, f"{order_item.menu_item.name} removed from cart")
                return redirect('cart')
            elif action == 'update_instructions':
                special_instructions = request.POST.get('special_instructions', '')
                order_item.special_instructions = special_instructions
                order_item.save()
                logger.info(f"Updated instructions for order item {order_item.id} for {request.user.username}")
                messages.info(request, f"Instructions updated for {order_item.menu_item.name}")
        except Exception as e:
            logger.error(f"Error updating cart for {request.user.username}: {str(e)}")
            messages.error(request, "An error occurred while updating your cart.")
        
        return redirect('cart')

class PromotionView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            promotions = Promotion.objects.filter(
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )
            form = PromotionForm()
            logger.debug(f"Promotion page accessed by {request.user.username}")
            return render(request, 'app/promotion.html', {
                'promotions': promotions,
                'form': form
            })
        except Exception as e:
            logger.error(f"Error loading promotions page: {str(e)}")
            messages.error(request, "An error occurred while loading promotions.")
            return render(request, 'app/promotion.html', {'promotions': [], 'form': PromotionForm()})

    def post(self, request):
        try:
            order = Order.get_pending_order(request.user)
            form = PromotionForm(request.POST)
            
            if form.is_valid():
                code = form.cleaned_data['code']
                try:
                    promotion = Promotion.objects.get(
                        promo_code=code,
                        is_active=True,
                        start_date__lte=timezone.now(),
                        end_date__gte=timezone.now()
                    )
                    
                    if order.promotions.filter(id=promotion.id).exists():
                        logger.warning(f"Duplicate promotion attempt by {request.user.username} for code {code}")
                        messages.warning(request, "This promotion is already applied")
                    else:
                        order.promotions.add(promotion)
                        order.save()
                        logger.info(f"Promotion {promotion.name} applied by {request.user.username}")
                        messages.success(request, f"Promotion '{promotion.name}' applied successfully!")
                except Promotion.DoesNotExist:
                    logger.warning(f"Invalid promotion code {code} attempted by {request.user.username}")
                    messages.error(request, "Invalid or expired promotion code")
        except Exception as e:
            logger.error(f"Error applying promotion by {request.user.username}: {str(e)}")
            messages.error(request, "An error occurred while applying the promotion.")
        
        return redirect('cart')

class RemovePromoView(LoginRequiredMixin, View):
    def post(self, request, promo_id):
        try:
            order = Order.get_pending_order(request.user)
            promotion = get_object_or_404(Promotion, id=promo_id)
            
            if promotion in order.promotions.all():
                order.promotions.remove(promotion)
                order.save()
                logger.info(f"Promotion {promotion.name} removed by {request.user.username}")
                messages.success(request, f"Promotion '{promotion.name}' removed")
        except Exception as e:
            logger.error(f"Error removing promotion {promo_id} by {request.user.username}: {str(e)}")
            messages.error(request, "An error occurred while removing the promotion.")
        
        return redirect('cart')

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            order = Order.get_pending_order(request.user)
            if not order.items.exists():
                messages.warning(request, "Your cart is empty")
                return redirect('menu')
            
            context = {
                'order': order,
                'form': CheckoutForm(initial=self._get_initial_data(request)),
                'delivery_charge': Decimal('2.00'),
            }
            return render(request, 'app/checkout.html', context)
            
        except Exception as e:
            logger.error(f"Checkout error: {str(e)}")
            messages.error(request, "Error loading checkout page")
            return redirect('cart')

    def post(self, request):
        try:
            order = Order.get_pending_order(request.user)
            form = CheckoutForm(request.POST)
            
            if not form.is_valid():
                return self._render_invalid_form(order, form)
            
            self._update_order(order, form)
            return self._process_standard_payment(order)
            
        except Exception as e:
            logger.error(f"Checkout error: {str(e)}")
            messages.error(request, "Error processing your order")
            return redirect('checkout')

    def _get_initial_data(self, request):
        return {
            'delivery_address': request.user.address,
            'contact_phone': request.user.phone_number,
        }

    def _render_invalid_form(self, order, form):
        context = {
            'order': order,
            'form': form,
            'delivery_charge': Decimal('10.00'),
        }
        return render(request, 'app/checkout.html', context)

    def _update_order(self, order, form):
        order.update_from_form(form)
        if form.cleaned_data.get('save_address'):
            self.request.user.update_address(
                form.cleaned_data['delivery_address'],
                form.cleaned_data['contact_phone']
            )

    def _process_standard_payment(self, order):
        order.complete_payment()
        messages.success(request, "Order placed successfully!")
        return redirect('order_history', order_id=order.id)

class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'app/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        try:
            logger.debug(f"Order history accessed by {self.request.user.username}")
            return Order.objects.filter(user=self.request.user).exclude(status='pending').order_by('-created_at')
        except Exception as e:
            logger.error(f"Error retrieving order history for {self.request.user.username}: {str(e)}")
            return Order.objects.none()

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'app/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['delivery_charge'] = Decimal('2.00')
            logger.debug(f"Order detail viewed for order {self.object.id}")
        except Exception as e:
            logger.error(f"Error getting order detail context: {str(e)}")
        return context

class TrackOrderView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id, user=request.user)
            logger.debug(f"Order tracking viewed for order {order_id} by {request.user.username}")
            return render(request, 'app/track_order.html', {'order': order})
        except Exception as e:
            logger.error(f"Error tracking order {order_id} by {request.user.username}: {str(e)}")
            messages.error(request, "An error occurred while tracking your order.")
            return redirect('order_history')

class ContactView(View):
    def get(self, request):
        try:
            form = ContactForm()
            logger.debug("Contact form page accessed")
            return render(request, 'app/contact.html', {'form': form})
        except Exception as e:
            logger.error(f"Error loading contact form: {str(e)}")
            return render(request, 'app/contact.html', {'form': ContactForm()})
    
    def post(self, request):
        try:
            form = ContactForm(request.POST)
            if form.is_valid():
                contact = form.save(commit=False)
                if request.user.is_authenticated:
                    contact.user = request.user
                contact.save()
                logger.info(f"New contact message from {contact.email}")
                messages.success(request, "Thank you for your message! We'll get back to you soon.")
                return redirect('home')
            
            logger.warning(f"Invalid contact form submission")
            return render(request, 'app/contact.html', {'form': form})
        except Exception as e:
            logger.error(f"Error processing contact form: {str(e)}")
            messages.error(request, "An error occurred while sending your message.")
            return render(request, 'app/contact.html', {'form': form})

class SearchView(View):
    def get(self, request):
        try:
            query = request.GET.get('q', '').strip()
            results = []
            
            if query:
                results = MenuItem.objects.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(category__name__icontains=query),
                    is_available=True
                ).distinct().order_by('category__display_order', 'name')
                logger.debug(f"Search performed for '{query}' returning {results.count()} results")
            
            categories = Category.objects.filter(
                is_active=True
            ).annotate(
                menu_items_count=Count('menu_items', filter=Q(menu_items__is_available=True)))
            
            context = {
                'query': query,
                'results': results,
                'results_count': results.count() if query else 0,
                'categories': categories,
            }
            return render(request, 'app/search_results.html', context)
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            messages.error(request, "An error occurred during search.")
            return render(request, 'app/search_results.html', {'query': '', 'results': [], 'categories': []})

class DeleteReviewView(LoginRequiredMixin, DeleteView):
    model = Review
    success_url = reverse_lazy('menu')
    
    def get_queryset(self):
        try:
            logger.debug(f"Review deletion attempted by {self.request.user.username}")
            return super().get_queryset().filter(user=self.request.user)
        except Exception as e:
            logger.error(f"Error in review deletion: {str(e)}")
            return Review.objects.none()
    
    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            logger.info(f"Review {kwargs['pk']} deleted by {request.user.username}")
            messages.success(request, "Your review has been deleted.")
            return response
        except Exception as e:
            logger.error(f"Error deleting review: {str(e)}")
            messages.error(request, "An error occurred while deleting your review.")
            return redirect(self.success_url)