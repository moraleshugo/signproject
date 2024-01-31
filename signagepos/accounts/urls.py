# accounts/urls.py

from django.urls import path
from .views import custom_admin_login, admin_dashboard, custom_logout, customer_list, create_customer, delete_customer, edit_customer, update_totals

app_name = 'customer'


urlpatterns = [
    #path('login/', custom_login, name='login'),
    path('', custom_admin_login, name='custom_admin_login'),
    path('logout', custom_logout, name='custom_logout'),
    path('dashboard', admin_dashboard, name='admin_dashboard'),
    # path('filter_by_year/<int:year>/', filter_by_year, name='filter_by_year'),
    path('customer/', customer_list, name='customer_list'),
    path('customer/create/', create_customer, name='create_customer'),
    path('customer/delete/<int:customer_id>/', delete_customer, name='delete_customer'),
     path('edit_customer/<int:customer_id>/', edit_customer, name='edit_customer'),
    path('update_totals/', update_totals, name='update_totals'),

    # Add other URL patterns as needed
]
