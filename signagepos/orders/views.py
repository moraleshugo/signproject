from django.contrib import messages
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderForm, CustomerForm, OrderImagesForm
from accounts.models import CustomUser
from .models import Order, OrderImage
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.http import JsonResponse

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

@login_required
def order_list(request):

    all_orders = Order.objects.all().order_by('-created_on')
    new_orders = Order.objects.filter(process_status='new')
    to_do_orders = Order.objects.filter(process_status='to_do')
    in_progress_orders = Order.objects.filter(process_status='in_progress')
    done_orders = Order.objects.filter(process_status='done')

     # Get all distinct months and years from the Order model
    distinct_months = Order.objects.dates('created_on', 'month').distinct()
    distinct_years = Order.objects.dates('created_on', 'year').distinct()

    # Extract month and year values
    month_choices = [(str(month.month), month.strftime('%B')) for month in distinct_months]
    year_choices = [(str(year.year), str(year.year)) for year in distinct_years]
    process_status_choices = Order.PROCESS_STATUS_CHOICES

   
     # Filter orders for the current yearfor all Completed orders
    current_year = timezone.now().year
    done_orders_current_year = done_orders.filter(created_on__year=current_year)

    # Get a list of distinct years from the orders
    available_years = Order.objects.dates('created_on', 'year')
    
    # Get the values from the query parameters
    month_param = request.GET.get('month', 'all')
    print("selected Month", month_param )
    year_param = request.GET.get('year', 'all')
    print("selected Year", year_param)
    process_status_param = request.GET.get('process_status', 'all')
    print("selected Status", process_status_param)
    
   # Extract the month name from the parameter value
    if month_param.startswith('month-'):
        selected_month = month_param[len('month-'):]
    else:
        selected_month = 'all'

    # Extract the Year name from the parameter value
    if year_param.startswith('year-'):
        selected_year = year_param[len('year-'):]
    else:
        selected_year = 'all'

    # Extract the Process Status from the parameter value
    if process_status_param.startswith('status-'):
        selected_status = process_status_param[len('status-'):]
    else:
        selected_status = 'all'

    # Filter orders based on the selected values
    filtered_orders = Order.objects.all()

    if selected_month != 'all':
        # Add filtering condition for month
        filtered_orders = filtered_orders.filter(created_on__month=int(selected_month))

    if selected_year != 'all':
        # Add filtering condition for year
        filtered_orders = filtered_orders.filter(created_on__year=int(selected_year))
    

    if selected_status != 'all':
        # Add filtering condition for process status
        filtered_orders = filtered_orders.filter(process_status=selected_status)

    

     # Get the search query from the request's GET parameters
    search_query = request.GET.get('search_query')
    print(search_query)

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

    
    return render(request, 'orders/order_list.html', {
        'months_dict': months_dict,
        
        'all_orders_page': all_orders_page,
        'new_orders': new_orders,
        'to_do_orders': to_do_orders,
        'in_progress_orders': in_progress_orders,
        'done_orders': done_orders_current_year,
        
        'month_choices': month_choices,
        'year_choices': year_choices,
        'process_status_choices': process_status_choices,
        
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_status': selected_status,
        #'selected_month_name': selected_month_name
        
        })



@login_required
def create_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST, request.FILES)
        customer_form = CustomerForm(request.POST)
        order_images_form = OrderImagesForm(request.POST, request.FILES)  # Initialize order_images_form

        if order_form.is_valid() and customer_form.is_valid() and order_images_form.is_valid():
            email = customer_form.cleaned_data['email'].lower()  # Convert email to lowercase
            first_name = customer_form.cleaned_data['first_name']
            
            last_name = customer_form.cleaned_data['last_name']
            print(first_name, last_name)
            # Check if a user with the provided email already exists
            existing_user = CustomUser.objects.filter(email=email).first()
            
            if existing_user:
                print('the user exists')
                if request.user.is_admin:
                    print('the user is admin')
                # Admin is creating the order, create a new user
                    customer = CustomUser.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        username=email,
                        email=email,
                        phone_number=customer_form.cleaned_data['phone_number'],
                    )
                    print(customer)
                    customer.save()
                else:
                    # Non-admin user is creating the order, assign the existing user
                    customer = existing_user
                
            else:
                # Create a new customer
                customer = CustomUser.objects.create(
                    first_name=customer_form.cleaned_data['first_name'],
                    last_name=customer_form.cleaned_data['last_name'],
                    username=email,
                    email=email,
                    phone_number=customer_form.cleaned_data['phone_number'],
                )
                customer.save()

            # Create a new order and associate it with the customer
            order = order_form.save(commit=False)
            order.customer = customer  # Assign the existing or newly created customer to the order
            order.order_status = 'new_order'
            order.process_status = 'new'
            order.created_on = timezone.now()
            order.save()

            # Save order images only if there are any provided
            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    OrderImage.objects.create(order=order, order_images=image, original_file_name=image.name)

            return redirect('orders:order_detail', order_number=order.order_number)

        else:
            # If forms are not valid, collect error messages and display them
            error_messages = []
            for form in [order_form, customer_form, order_images_form]:
                for field, errors in form.errors.items():
                    error_messages.append(f"{form.fields[field].label}: {', '.join(errors)}")

            for message in error_messages:
                messages.error(request, message)
    else:
        order_form = OrderForm()
        customer_form = CustomerForm()
        order_images_form = OrderImagesForm()

    return render(request, 'orders/create_order.html', {'order_form': order_form, 'customer_form': customer_form, 'order_images_form': order_images_form})



@login_required
def edit_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':

        order_form = OrderForm(request.POST, instance=order)
        customer_form = CustomerForm(request.POST or None, instance=order.customer, prefix='customer')
        #order_images_form = OrderImagesForm(request.POST, request.FILES, instance=order.orderimage)
        

        if order_form.is_valid() and customer_form.is_valid():
            order_instance = order_form.save(commit=False)
            customer_instance = customer_form.save(commit=False)
            #order_images_instance = order_images_form.save(commit=False)

            # Calculate warranty_end_date from the form data
            warranty_start_date = order_form.cleaned_data.get('warranty_start_date')
            warranty_duration_str = request.POST.get('warranty_duration', '')
            if warranty_start_date and warranty_duration_str:
                warranty_duration_in_months = int(warranty_duration_str)
                warranty_end_date = warranty_start_date + relativedelta(months=warranty_duration_in_months)
                order_instance.warranty_end_date = warranty_end_date
            else:
                order_instance.warranty_end_date = None
            
            # Associate the order with the customer
            order_instance.customer = customer_instance

           

            # Save the instances
            order_instance.save()
            customer_instance.save()
            #order_images_instance.save()

            # Show success message
            messages.success(request, 'Order successfully edited.')

            return redirect('orders:order_detail', order_number=order_instance.order_number)
        else:
            # Show error message
            messages.error(request, 'Error editing the order. Please check the form.')


    else:
        order_form = OrderForm(instance=order)
        

        customer_form = CustomerForm(instance=order.customer or None, prefix='customer', initial={'email': order.customer.email})
        


    return render(request, 'orders/edit_order.html', {'order_form': order_form, 'customer_form': customer_form, 'order': order})

@login_required   
def delete_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    # Delete the order regardless of the HTTP method
    order.delete()
    
    return redirect('orders:order_list')


@login_required
def complete_order(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        
        # Assuming you have a model named YourOrderModel
        try:
            order = Order.objects.get(order_number=order_number)
        except YourOrderModel.DoesNotExist:
            return HttpResponse('Order not found', status=404)
        
        # Update order status and process status
        order.order_status = 'Completed'
        order.process_status = 'done'
        order.deposit = 0
        order.save()

        # Redirect to the order detail page or any other page as needed
        return redirect('orders:order_detail', order_number=order.order_number)
    else:
        # Handle invalid request method
        return HttpResponse('Invalid request method', status=405)
    
    

@login_required
def order_detail(request, order_number):
    user = request.user

    # Check if the user is an admin
    is_admin = CustomUser.objects.filter(username=user.username, is_admin=True).exists()



    order = get_object_or_404(Order, order_number=order_number)

    # Filter non-mockup images
    non_mockup_images = order.orderimage_set.filter(is_mockup=False)
    mockup_images = order.orderimage_set.filter(is_mockup=True)

    

    return render(request, 'orders/order_detail.html', {'order': order, 'is_admin': is_admin, 'non_mockup_images': non_mockup_images, 'mockup_images': mockup_images})
    


   

# def start_order(request, order_number):
#     order = get_object_or_404(Order, order_number=order_number)
#     order.process_status = 'to_do'
#     order.save()

#     messages.success(request, 'Order successfully started!')

#     return redirect('orders:order_list')


# def start_progress(request, order_number):
#     order = get_object_or_404(Order, order_number=order_number)
#     order.process_status = 'in_progress'
#     order.save()

#     messages.success(request, 'Order progress successfully started!')

#     return redirect('orders:order_list')

@login_required
def transition_order_status(request, order_number, new_status):
    order = get_object_or_404(Order, order_number=order_number)

    # Assuming you have a valid list of allowed status transitions
    allowed_transitions = ['to_do', 'in_progress', 'done']

    if new_status in allowed_transitions:
        order.process_status = new_status
        order.save()

        # Display a custom message based on the new status
        status_messages = {
            'to_do': 'Order successfully moved to To Do!',
            'in_progress': 'Order is now In Progress!',
            'done': 'Order marked as Complete!',
            # Add other statuses as needed
        }

        messages.success(request, status_messages.get(new_status, 'Status transition successful!'))
    else:
        messages.error(request, 'Invalid status transition.')

    return redirect('orders:order_list')

@login_required
def mark_remainder_paid(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    # Set the deposit to the same amount as the price
    order.deposit = order.price

    # Perform any additional logic here if needed

    # Save the changes
    order.save()

    # Redirect to the order detail page or any other desired page
    return redirect('orders:order_list')

@login_required
def upload_mockup(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if request.method == 'POST':
        # Handle the uploaded mockups here
        # You can access the uploaded files using request.FILES['images']
        # Process the files and save them as needed

        # Example: Save each uploaded file
        for image in request.FILES.getlist('images'):
           OrderImage.objects.create(order=order, order_images=image, original_file_name=image.name, is_mockup=True )

        # Display a success message
        messages.success(request, 'Mockups uploaded successfully.')

        # Redirect to the page where you want to go after uploading
        return redirect('order:edit_order', order_number=order.order_number)

    # Render the upload mockups page
    # Display a success message
    messages.success(request, 'Oops Something went wrong!')
    return redirect('orders:order_detail', order_number=order.order_number)  # Create a template for this page if needed

@login_required
def upload_images(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        # Check if it's mockup or sign images
        if 'mockupImages' in request.FILES:
            is_mockup = True
            images_key = 'mockupImages'
        elif 'signImages' in request.FILES:
            is_mockup = False
            images_key = 'signImages'
        else:
            # Handle the case where no files are provided
            messages.error(request, 'No images provided.')
            return redirect('orders:edit_order', order_number=order.order_number)

        # Handle the uploaded images
        images = request.FILES.getlist(images_key)
        
        # Example: Save each uploaded file
        for image in images:
            OrderImage.objects.create(order=order, order_images=image, original_file_name=image.name, is_mockup=is_mockup)

        # Display a success message
        messages.success(request, 'Images uploaded successfully.')

        # Redirect to the page where you want to go after uploading
        return redirect('orders:edit_order', order_number=order.order_number)

    # Render the upload images page
    # Display an error message
    messages.error(request, 'Oops! Something went wrong.')
    return redirect('orders:edit_order', order_number=order.order_number)

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(OrderImage, id=image_id)
    order_id = image.order.id  # Save order ID before deleting the image
    image.delete()

    # Send a JSON response indicating success
    return JsonResponse({'success': True, 'order_id': order_id})

def invoice_receipt(request, order_number):
    # Retrieve the order details based on the order_id
    try:
        order = Order.objects.get(order_number=order_number)
         # Calculate total price
        total_price = order.price * order.quantity

        # Calculate total cost including other expenses
        total_cost = total_price + order.other_expenses
        
    except Order.DoesNotExist:
        # Handle the case where the order doesn't exist
        # You can customize this based on your requirements
        return render(request, 'orders/invoice_not_found.html')

    # Pass the order object to the template
    context = {'order': order, 
        'total_price': total_price,
        'total_cost': total_cost,}
    return render(request, 'orders/invoice_receipt.html', context)