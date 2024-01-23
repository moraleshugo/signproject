 # accounts/views.py

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from accounts.models import CustomUser
from .forms import CustomerCreationForm, CustomerEditForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




def custom_admin_login(request):
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

    return render(request, 'accounts/custom_admin_login.html')

def custom_logout(request):
    logout(request)
    return redirect('customer:custom_admin_login')


def admin_dashboard(request):
    pass
    return render(request, 'accounts/admin_dashboard.html')

@login_required  # This decorator ensures that only authenticated users can access this view
def customer_list(request):
    customers = CustomUser.objects.all()


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

    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer:customer_list')  # Replace 'customer_list' with the actual URL name for the customer list page

    return render(request, 'accounts/delete_customer.html', {'customer': customer})


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