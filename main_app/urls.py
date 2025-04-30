from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import DeleteReviewView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('promotions/', views.PromotionView.as_view(), name='promotions'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('menu/category/<slug:category_slug>/', views.MenuView.as_view(), name='menu_category'),
    path('menu/item/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu_item_detail'),
    
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:item_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),

    path('orders/', views.OrderHistoryView.as_view(), name='order_history'),
    path('orders/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('reviews/delete/<int:pk>/', DeleteReviewView.as_view(), name='delete_review'),
    
   
    path('search/', views.SearchView.as_view(), name='search'),

    path('about/', views.about , name = 'about'),
    path('contact/', views.contact, name = 'contact'),
 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
