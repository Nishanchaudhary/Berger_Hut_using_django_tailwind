from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home , name='home'),
    path('menu/', views.menu , name='menu'),
    path('create_order/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/remove_item/<int:item_id>/', views.remove_order_item, name='remove_order_item'),
    path('about/', views.about , name = 'about'),
    path('contact/', views.contact, name = 'contact'),
    path('user_login/', views.user_login, name = 'user_login'),
    path('register/', views.register, name= 'register'),
    path('user_logout/', views.user_logout, name='user_logout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
