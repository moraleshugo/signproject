from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderForm, CustomerForm, OrderImagesForm
from accounts.models import CustomUser
from .models import Order, OrderImage
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.http import JsonResponse


def order_list(request):
    all_orders = Order.objects.all()
    new_orders = Order.objects.filter(process_status='new')
    to_do_orders = Order.objects.filter(process_status='to_do')
    in_progress_orders = Order.objects.filter(process_status='in_progress')
    done_orders = Order.objects.filter(process_status='done')

     # Filter orders for the current yearfor all Completed orders
    current_year = timezone.now().year
    done_orders_current_year = done_orders.filter(created_on__year=current_year)

    # Get a list of distinct years from the orders
    available_years = Order.objects.dates('created_on', 'year')
    
    # Get the selected year from the request's GET parameters
    selected_year = request.GET.get('selected_year')
    
    # Get all orders or filter by the selected year
    if selected_year and selected_year != 'all':
        all_orders = Order.objects.filter(created_on__year=selected_year)
    else:
        all_orders = Order.objects.all()


    # Set the number of items per page
    items_per_page = 10

    # Create a Paginator instance for all orders
    paginator = Paginator(all_orders, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    # Get the specified page for all orders
    try:
        all_orders_page = paginator.page(page)
    except PageNotAnInteger:
        all_orders_page = paginator.page(1)
    except EmptyPage:
        all_orders_page = paginator.page(paginator.num_pages)

    # Extract first and last letters of the first name for each order
    # for status, order_list in orders.items():
    #     for order in order_list:
    #         first_name = order.customer.first_name
    #         last_name = order.customer.last_name

    #         # Add first and last name initials to the order as additional attributes
    #         order.first_name_initial = first_name[0] if first_name else ''
    #         order.last_name_initial = last_name[0] if last_name else ''

    return render(request, 'orders/order_list.html', {
        
        'all_orders_page': all_orders_page,
        'new_orders': new_orders,
        'to_do_orders': to_do_orders,
        'in_progress_orders': in_progress_orders,
        'done_orders': done_orders_current_year,
        'selected_year': selected_year,
        'available_years': available_years,})



def create_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST, request.FILES)
        customer_form = CustomerForm(request.POST)
        order_images_form = OrderImagesForm(request.POST, request.FILES)  # Initialize order_images_form

        if order_form.is_valid() and customer_form.is_valid() and order_images_form.is_valid():
            email = customer_form.cleaned_data['email']

            # Check if a user with the provided email already exists
            existing_user = CustomUser.objects.filter(email=email).first()
            
            if existing_user:

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
            order.order_status = 'New Order'
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

            return redirect('orders:order_detail', order_number=order_instance.order_number)

    else:
        order_form = OrderForm(instance=order)
        

        customer_form = CustomerForm(instance=order.customer or None, prefix='customer', initial={'email': order.customer.email})
        


    return render(request, 'orders/edit_order.html', {'order_form': order_form, 'customer_form': customer_form, 'order': order})
    
def delete_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    if request.method == 'POST':
        order.delete()
        return redirect('orders:order_list')  # Redirect to the order list page or wherever you need to go

    return render(request, 'orders/confirm_delete.html', {'order': order})


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

def delete_image(request, image_id):
    image = get_object_or_404(OrderImage, id=image_id)
    order_id = image.order.id  # Save order ID before deleting the image
    image.delete()

    # Send a JSON response indicating success
    return JsonResponse({'success': True, 'order_id': order_id})