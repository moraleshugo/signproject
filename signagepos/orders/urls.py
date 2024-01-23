from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import order_list, create_order, order_detail, edit_order, delete_order, transition_order_status, complete_order, upload_images, delete_image

app_name = 'orders'

urlpatterns = [
    path('orders/', order_list, name='order_list'),
    path('orders/create/', create_order, name='create_order'),
    path('orders/<str:order_number>/', order_detail, name='order_detail'),
    path('orders/edit/<str:order_number>/', edit_order, name='edit_order'),
    path('orders/delete/<str:order_number>/', delete_order, name='delete_order'),
    path('complete_order', complete_order, name='complete_order'),
    path('upload_images/<str:order_number>/', upload_images, name='upload_images'),
    path('delete_image/<int:image_id>/', delete_image, name='delete_image'),
    # path('start_order/<str:order_number>/', start_order, name='start_order'),
    # path('start_in_progress/<str:order_number>/', start_order, name='start_order'),
    path('transition_status/<str:order_number>/<str:new_status>/', transition_order_status, name='transition_order_status'),
    #path('<str:order_number>/', start_progress, name='start_progress'),

    # Add other URLs as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)