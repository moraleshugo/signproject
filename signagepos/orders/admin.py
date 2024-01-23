from django.contrib import admin
from .models import Order, OrderImage

class OrderImageAdmin(admin.ModelAdmin):
    list_display = ['order', 'order_images']  # Add other fields you want to display in the order images list

admin.site.register(OrderImage, OrderImageAdmin)


class OrderImagesInline(admin.TabularInline):
    model = OrderImage
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderImagesInline]
    list_display = ('order_number', 'design_notes', 'customer', 'width', 'height', 'color', 'cut_type', 'order_status')
    search_fields = ('order_number', 'design_notes', 'customer__username', 'customer__email')

    def get_order_images(self, obj):
        images = OrderImage.objects.filter(order=obj)
        return ', '.join([str(img.order_images) for img in images])

    get_order_images.short_description = 'Order Images'
    
    readonly_fields = ['get_order_images']  # Make the images readonly in the detail view

admin.site.register(Order, OrderAdmin)