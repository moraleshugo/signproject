from orders.models import Order
from accounts.models import CustomUser
from django.utils import timezone
from django.contrib.auth import get_user_model
from faker import Faker
import random


num_orders = 30


fake = Faker()
User = get_user_model()

COLOR_CHOICES = [
    ('Cool White', 'Cool White'),
    ('Warm White', 'Warm White'),
    ('Yellow', 'Yellow'),
    ('Orange', 'Orange'),
    ('Red', 'Red'),
    ('Pink', 'Pink'),
    ('Hot Pink', 'Hot Pink'),
    ('Purple', 'Purple'),
    ('Blue', 'Blue'),
    ('Ice Blue', 'Ice Blue'),
    ('Green', 'Green'),
    # Add more colors as needed
]

CUT_TYPE_CHOICES = [
    ('Cut to Shape', 'Cut to Shape'),
    ('Square/Rectangle', 'Square/Rectangle'),
    ('Cut to Letter', 'Cut to Letter'),
    ('Circular/Round', 'Circular/Round'),
    # Add more cut types as needed
]

def create_random_customer():
    return User.objects.create(
        username=fake.user_name(),
        email=fake.email(),
        phone_number=fake.phone_number(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        # Add other fields from CustomUser model as needed
    )

ORDER_STATUS_CHOICES = [
        ('New Order', 'New Order'),
        ('In Progress', 'In Progress'),
        ('Needs Design', 'Needs Design'),
        ('Design Ready', 'Design Ready'),
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Shipped', 'Shipped'),
        ('Cancelled', 'Cancelled'),
        ('Awaits Pickup', 'Awaits Pickup'),
        ('Delivered', 'Delivered'),
        ('Complete', 'Complete'),
        ]
PROCESS_STATUS_CHOICES = [
    ('new', 'New Order'),
    ('to_do', 'To Do'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    # Add other statuses as needed
    ]

# Assuming Order is the name of your model
for _ in range(num_orders):
    customer = create_random_customer()

    # Generate order number with the format Year_000001
    current_year = timezone.now().year
    order_number = f'{current_year}_{str(_ + 1).zfill(6)}'

    # Check if the order number already exists
    while Order.objects.filter(order_number=order_number).exists():
        _ += 1
        order_number = f'{current_year}_{str(_ + 1).zfill(6)}'

    new_order = Order.objects.create(
        customer=customer,
        width=fake.random_int(min=1, max=100),
        height=fake.random_int(min=1, max=100),
        color=random.choice(COLOR_CHOICES)[0],
        design_notes=fake.text(max_nb_chars=100),
        cut_type=random.choice(CUT_TYPE_CHOICES)[0],
        is_business=fake.boolean(),
        order_number=order_number,
        shipping_address=fake.address(),
        city=fake.city(),
        state=fake.state_abbr(),
        zip_code=fake.zipcode(),
        quantity=fake.random_int(min=1, max=10),
        deposit=42.0,
        price=150.0,
        order_status='New Order',
        process_status='new',
        tracking_number=get_random_string(length=12),
        company_notes=fake.text(max_nb_chars=50),
        acrylic_cost=25.0,
        silicone_cost=40.0,
        silicone_amount_meters=5.0,
        led_light_cost=50.0,
        led_light_meters=10.0,
        power_supply_cost=20.0,
        mounting_accessories_cost=30.0,
        created_on=timezone.now(),
    )
