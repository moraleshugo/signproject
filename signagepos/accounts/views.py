 # accounts/views.py

from django.http import JsonResponse
from django.db.models import Count, Case, When, Value, IntegerField
from django.db.models import Q
from django.contrib import messages
from django.db.models import Min, Max
from collections import defaultdict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from accounts.models import CustomUser
from .forms import CustomerCreationForm, CustomerEditForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.utils import timezone
from orders.models import Order
from .utils import calculate_total_profit, get_total_order_count, get_total_orders_current_year, calculate_total_sales, calculate_total_cost
import datetime
from decimal import Decimal
import calendar
from datetime import timedelta
from datetime import datetime




months_dict = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}


def custom_admin_login(request):
    if request.user.is_authenticated:
        return redirect('customer:admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user)

            # Redirect to a success page or dashboard
            return redirect('customer:admin_dashboard')  # Change 'admin-dashboard' to the desired URL name

        else:
            # Display an error message
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'authentication/login.html')

def custom_logout(request):
    logout(request)
    return redirect('customer:custom_admin_login')

@login_required
def admin_dashboard(request):
    # Get all orders
    all_orders = Order.objects.all()
    # Get the current year
    current_year = datetime.now().year

     # Get all distinct months from January to December
    months = range(1, 13)
    
    # Convert month numbers to month names
    month_names = [datetime.strptime(str(month), "%m").strftime("%B") for month in months]

    # Get the minimum and maximum order years
    min_year = Order.objects.aggregate(Min('created_on'))['created_on__min'].year
    max_year = Order.objects.aggregate(Max('created_on'))['created_on__max'].year

    # Create a list of years from min_year to max_year
    years = list(range(min_year, max_year + 1))

   

    # Get the selected year and month from the query parameters
    selected_year = request.GET.get('selected_year', 'all')
    selected_month = request.GET.get('selected_month')

    # Ensure selected_year and selected_month are valid numeric values

    
    # try:
    #     selected_year = int(selected_year)
    # except (TypeError, ValueError):
    #     selected_year = timezone.now().year

    # Ensure selected_month is a valid numeric value, or set it to January if None
    # try:
    #     selected_month = int(selected_month)
    # except (TypeError, ValueError):
    #     selected_month = 1  # January
    if selected_month:
        selected_month = int(selected_month)
        print("selected Month", selected_month)
    else:
        selected_month = 1
    
    if selected_year:
        selected_year = selected_year
        print("selected year",selected_year)
    else:
        selected_year = 'all'


    filtered_orders = Order.objects.all()


    if selected_month:
        # Add filtering condition for month
        filtered_orders = filtered_orders.filter(created_on__month=selected_month)
        print(filtered_orders)
    if selected_year != 'all':
    # Add filtering condition for year
        filtered_orders = filtered_orders.filter(created_on__year=selected_year)
    

    # Get the search query from the request's GET parameters
    search_query = request.GET.get('search_query')
    

    # Filter orders based on the search query
    if search_query:
        filtered_orders = all_orders.filter(Q(design_notes__icontains=search_query) |
            Q(order_number__icontains=search_query) |
            Q(color__icontains=search_query) |
            Q(cut_type__icontains=search_query) |
            Q(order_status__icontains=search_query) |
            Q(process_status__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(shipping_address__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(zip_code__icontains=search_query) |
            Q(tracking_number__icontains=search_query)
            )
        print(filtered_orders)
    
    # If specific year and month are selected, filter orders by them
    # if selected_year is not None and selected_month is not None:
    #     orders_by_month = Order.objects.filter(created_on__year=selected_year, created_on__month=selected_month)
    #     total_history_past_orders = orders_by_month.count()
    # elif selected_year is not None:
    #     orders_by_month = Order.objects.filter(created_on__year=selected_year)
    #     total_history_past_orders = orders_by_month.count()
    # elif selected_month is not None:
    #     orders_by_month = Order.objects.filter(created_on__month=selected_month)
    #     total_history_past_orders = orders_by_month.count()
    # else:
    #     orders_by_month = Order.objects.all()
    #     total_history_past_orders = orders_by_month.count()
    orders_by_month = Order.objects.all()
    total_history_past_orders = orders_by_month.count()
    # Calculate total sales, total cost, and total profit for the selected month or all months
    total_history_past_sales = filtered_orders.aggregate(Sum('price'))['price__sum'] or 0
    total_history_past_cost = filtered_orders.aggregate(Sum('total_sign_material_cost'))['total_sign_material_cost__sum'] or 0
    total_history_past_profit = filtered_orders.aggregate(Sum('total_sign_profit'))['total_sign_profit__sum'] or 0

   
       
    # All History SALES
    total_profit = calculate_total_profit()
    total_order_count = get_total_order_count()
    total_sales = calculate_total_sales()
    total_cost = calculate_total_cost()

    # Total Year Orders
    total_orders_current_year = get_total_orders_current_year()

    monthly_profit_data = []
    monthly_sales_data = []
    monthly_cost_data = []

    # Calculate total profit for each month of the current year
    months = range(1, 13)  # 1 to 12 representing January to December

    for month in months:
        
        start_date = timezone.datetime(current_year, month, 1)

        # Check if the current month is December
        if month == 12:
            end_date = timezone.datetime(current_year + 1, 1, 1) - timezone.timedelta(days=1)
        else:
            end_date = timezone.datetime(current_year, month + 1, 1) - timezone.timedelta(days=1)

        # Total profit for the month
        total_monthly_profit = Order.objects.filter(
            created_on__range=(start_date, end_date),
            total_sign_profit__isnull=False
        ).aggregate(Sum('total_sign_profit'))['total_sign_profit__sum'] or 0

        # Total cost for the month
        total_monthly_cost = Order.objects.filter(
            created_on__range=(start_date, end_date),
            total_sign_material_cost__isnull=False
        ).aggregate(Sum('total_sign_material_cost'))['total_sign_material_cost__sum'] or 0

        # Calculate total sales for the month
        total_monthly_sales = Order.objects.filter(
            created_on__range=(start_date, end_date),
            price__isnull=False  # Filter out orders without a price
        ).aggregate(Sum('price'))['price__sum'] or 0

        


        monthly_profit_data.append(float(total_monthly_profit))  # Convert to float
        monthly_cost_data.append(float(total_monthly_cost))
        monthly_sales_data.append(float(total_monthly_sales))  # Convert to float

    # Calculate total orders for the month
    total_monthly_orders = Order.objects.filter(
        created_on__range=(start_date, end_date)
    ).count()

    

    # Total cost for the year
    total_cost_year = sum(monthly_cost_data)
    # Total sales for the year
    total_sales_year = sum(monthly_sales_data)
    # Total profit for the year
    total_profit_year = sum(monthly_profit_data)

    

    # Set the number of items per page
    items_per_page = 10

    # Create a Paginator instance for all orders
    paginator = Paginator(filtered_orders, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    # Get the specified page for all orders
    try:
        all_orders_page = paginator.page(page)
    except PageNotAnInteger:
        all_orders_page = paginator.page(1)
    except EmptyPage:
        all_orders_page = paginator.page(paginator.num_pages)


    
    

    context = {
        'months_dict': months_dict,
        'month_names': month_names,

        'all_orders_page': all_orders_page,

        # OVERALL TOTAL ORDERS
        'total_profit': total_profit,
        'total_order_count': total_order_count,
        'total_sales': total_sales,
        'total_cost': total_cost,

        # TOTAL ORDERS FOR THE MONTH
        'monthly_profit_data': monthly_profit_data,
        'monthly_sales_data': monthly_sales_data,
        'monthly_cost_data': monthly_cost_data,
        

        'monthly_chart_year_sales_data': monthly_sales_data,
        'monthly_chart_year_profit_data': monthly_profit_data,

        # TOTAL ORDERS FOR THE YEAR
        'total_orders_current_year': total_orders_current_year,
        'total_profit_year': total_profit_year,
        'total_cost_year': total_cost_year,
        'total_sales_year': total_sales_year,
        'years': years,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'all_orders': all_orders,

        #History Past Orders Sales
        'total_history_past_sales': total_history_past_sales,
        'total_history_past_cost': total_history_past_cost,
        'total_history_past_profit': total_history_past_profit,
        'total_history_past_orders': total_history_past_orders
        

        
    }
    

    return render(request, 'accounts/admin_dashboard.html', context)




@login_required  # This decorator ensures that only authenticated users can access this view
def customer_list(request):
    search_query = request.GET.get('search_query')
     # Get all customers
    customers = CustomUser.objects.annotate(
        total_orders=Count('orders')
    )

    # Apply search query if provided
    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Order by admins first and then by total orders
    customers = customers.order_by(
        Case(
            When(is_admin=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        '-total_orders'  # Assuming you want to order by total orders in descending order
    )


    # Set the number of items per page
    items_per_page = 10

    # Create a Paginator instance for all orders
    paginator = Paginator(customers, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

     # Get the specified page for all orders
    try:
        all_customers_page = paginator.page(page)
    except PageNotAnInteger:
        all_customers_page = paginator.page(1)
    except EmptyPage:
        all_customers_page = paginator.page(paginator.num_pages)

    context = {
        'all_customers_page': all_customers_page,
        }
    return render(request, 'accounts/customers_page.html', context)


@login_required
def create_customer(request):
    if request.method == 'POST':
        customer_form = CustomerCreationForm(request.POST, prefix='customer')

        if customer_form.is_valid():
            # Save customer with the linked address
            customer = customer_form.save(commit=False)
            customer.save()

            # Add a success message
            messages.success(request, 'Customer created successfully.')

            return redirect('customer:customer_list')  # Replace 'customer_list' with the actual URL name for the customer list page
    else:
        customer_form = CustomerCreationForm(prefix='customer')

    return render(request, 'accounts/create_customer.html', {'customer_form': customer_form})

def delete_customer(request, customer_id):
    customer = get_object_or_404(CustomUser, id=customer_id)
    customer.delete()
    messages.success(request, 'Customer deleted successfully.')
    return redirect('customer:customer_list')  # Replace 'customer_list' with the actual URL name for the customer list page

    

@login_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(CustomUser, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerEditForm(request.POST, instance=customer)
        print(form)
        if form.is_valid():
            print("Form data before saving:", form.cleaned_data)
            form.save()
            print("Form data after saving:", form.cleaned_data)
            messages.success(request, 'Customer information updated successfully.')
            return redirect('customer:edit_customer', customer.id)
        else:
            messages.error(request, 'Failed to update customer information. Please check the form.')

    else:
        form = CustomerEditForm(instance=customer)

    return render(request, 'accounts/edit_customer.html', {'form': form, 'customer': customer})

@login_required
def update_totals(request):
    selected_month = int(request.POST.get('selected_month', None))

    # Calculate start and end dates for the selected month
    current_year = timezone.now().year

    start_date = timezone.datetime(current_year, selected_month, 1)
    if selected_month == 12:
        end_date = timezone.datetime(current_year + 1, 1, 1) - timezone.timedelta(days=1)
    else:
        end_date = timezone.datetime(current_year, selected_month + 1, 1) - timezone.timedelta(days=1)

    # Calculate total sales for the month
    total_monthly_sales = Order.objects.filter(
        created_on__range=(start_date, end_date),
        price__isnull=False
    ).aggregate(Sum('price'))['price__sum'] or 0

    # Calculate total cost for the month
    total_monthly_cost = Order.objects.filter(
        created_on__range=(start_date, end_date),
        total_sign_material_cost__isnull=False
    ).aggregate(Sum('total_sign_material_cost'))['total_sign_material_cost__sum'] or 0

    # Calculate total profit for the month
    total_monthly_profit = Order.objects.filter(
        created_on__range=(start_date, end_date),
        total_sign_profit__isnull=False
    ).aggregate(Sum('total_sign_profit'))['total_sign_profit__sum'] or 0

    # Calculate total orders for the month
    monthly_total_orders = Order.objects.filter(
        created_on__range=(start_date, end_date)
    ).count()


   
    previous_month_start = (start_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    previous_month_end = start_date.replace(day=1) - timedelta(days=1)

    # Calculate total sales for the previous month
    previous_month_revenue = Order.objects.filter(
        created_on__range=(previous_month_start, previous_month_end),
        price__isnull=False
    ).aggregate(Sum('price'))['price__sum'] or 0
    
    # Calculate total cost for the previous month
    previous_month_total_cost = Order.objects.filter(
        created_on__range=(previous_month_start, previous_month_end),
        total_sign_material_cost__isnull=False
    ).aggregate(Sum('total_sign_material_cost'))['total_sign_material_cost__sum'] or 0

    # Calculate total profit for the previous month
    previous_month_total_profit = Order.objects.filter(
        created_on__range=(previous_month_start, previous_month_end),
        total_sign_profit__isnull=False
    ).aggregate(Sum('total_sign_profit'))['total_sign_profit__sum'] or 0

    # Calculate total orders for the previous month
    previous_month_total_orders = Order.objects.filter(
        created_on__range=(previous_month_start, previous_month_end)
    ).count()



    print(previous_month_revenue)
    # Return the updated totals as JSON
    data = {
        'total_sales': total_monthly_sales,
        'total_cost': total_monthly_cost,
        'total_profit': total_monthly_profit,
        'total_orders': monthly_total_orders,
        'previous_month_revenue': previous_month_revenue,
        'previous_month_total_cost': previous_month_total_cost,
        'previous_month_total_profit': previous_month_total_profit,
        'previous_month_total_orders': previous_month_total_orders,
    }

    return JsonResponse(data)



    
