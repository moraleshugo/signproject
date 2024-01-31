# utils.py
from django.db.models import Sum
from orders.models import Order
from django.db.models import Count
import datetime

def calculate_total_profit():
    # Aggregate the sum of the profit field for all orders
    total_profit = Order.objects.aggregate(Sum('total_sign_profit'))['total_sign_profit__sum']
    return total_profit or 0  # Return 0 if there are no orders or profit is None


def get_total_order_count():
    # Get the count of all orders
    total_order_count = Order.objects.count()
    return total_order_count or 0

def calculate_total_cost():
    # Aggregate the sum of the material_cost field for all orders
    total_cost = Order.objects.aggregate(Sum('total_sign_material_cost'))['total_sign_material_cost__sum']
    
    return total_cost or 0  # Return 0 if there are no orders or cost is None



def calculate_total_sales():
    # Aggregate the sum of the price field for all orders
    total_sales = Order.objects.aggregate(Sum('price'))['price__sum']
    return total_sales or 0  # Return 0 if there are no orders or sales is None
    
#GET ORDERS FOR THE YEAR
def get_total_orders_current_year():
    # Get the count of orders for the current year
    current_year = datetime.datetime.now().year
    total_orders_current_year = Order.objects.filter(created_on__year=current_year).count()
    return total_orders_current_year or 0