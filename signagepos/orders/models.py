from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
import os

def order_image_path(instance, filename):
    # Get the order number and file extension
    order_number = str(instance.order.order_number)
    ext = filename.split('.')[-1]

    # Construct the file path
    filename = f"{order_number}.{ext}"

    # Return the final upload path
    return os.path.join('order_images', filename)

class Order(models.Model):
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
    ORDER_STATUS_CHOICES = [
        ('new_order', 'New Order'),
        ('in_progress', 'In Progress'),
        ('needs_design', 'Needs Design'),
        ('design_ready', 'Design Ready'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
        ('awaits_pickup', 'Awaits Pickup'),
        ('delivered', 'Delivered'),
        ('complete', 'Complete'),

    ]
    PROCESS_STATUS_CHOICES = [
        ('new', 'New Order'),
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        # Add other statuses as needed
    ]

    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, choices=COLOR_CHOICES)
    design_notes = models.CharField(max_length=255, blank=True, null=True)
    cut_type = models.CharField(max_length=255, choices=CUT_TYPE_CHOICES)
    is_business = models.BooleanField(default=False, blank=True, null=True)
    order_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    shipping_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1, blank=True, null=True)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, blank=True, null=True)
    process_status = models.CharField(max_length=20, choices=PROCESS_STATUS_CHOICES, default='new')
    warranty_start_date = models.DateField(blank=True, null=True)
    warranty_duration = models.DurationField(blank=True, null=True)
    warranty_end_date = models.DateField(blank=True, null=True)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    company_notes = models.TextField(blank=True)
    acrylic_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    silicone_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    silicone_amount_meters = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    led_light_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    led_light_meters = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    power_supply_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mounting_accessories_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

   
    created_on = models.DateTimeField(default=timezone.now)
    

    def save(self, *args, **kwargs):
        # Generate order number with the format Year_000001
        if not self.order_number:
            current_year = timezone.now().year
            last_order = Order.objects.filter(order_number__startswith=f"{current_year}_").order_by('-order_number').first()

            if last_order:
                order_number = str(int(last_order.order_number[-6:]) + 1).zfill(6)
            else:
                order_number = '000001'

            self.order_number = f"{current_year}_{order_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number}: {self.design_notes}"

    def total_material_cost(self):
        # Calculate the total cost of materials for this order
        total_cost = sum([
            self.acrylic_cost or 0,
            self.silicone_cost or 0,
            self.led_light_cost or 0,
            self.power_supply_cost or 0,
            self.mounting_accessories_cost or 0,
            self.other_expenses or 0,
        ])
        print(f"Intermediate values: {self.acrylic_cost}, {self.silicone_cost}, {self.led_light_cost}, {self.power_supply_cost}, {self.mounting_accessories_cost}")
        print(f"Total Material Cost: {total_cost}")
        return total_cost

    def total_material_amount(self):
        # Calculate the total amount of materials used for this order
        total_amount = sum([
            self.silicone_amount_meters or 0,
            self.led_light_meters or 0,
        ])
        return total_amount


    def get_balance_due(self):
        if self.price is not None and self.deposit is not None:
            balance_due = self.price - self.deposit
            if balance_due == self.price:
                balance_due = 0
            return max(balance_due, 0)  # Return 0 if balance_due is less than or equal to 0
        else:
            return 0



    def total_profit(self):
        # Calculate the total profit (price - total cost)
        total_cost = self.total_material_cost() or 0  # Replace 'or 0' with your default value
        return self.price - total_cost if self.price is not None else None

    def total_led_amps(self):
        # Calculate the total amps based on the amount of meters of LED light used (assuming 12V DC)
        watts_per_meter = 8.5
        volts = 12  # Voltage of the LED lights (adjust if different)
        total_led_meters = self.led_light_meters or 0
        total_led_watts = float(total_led_meters) * watts_per_meter
        amps = total_led_watts / volts
        rounded_amps = round(amps, 3)
        return rounded_amps
        
class OrderImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_images = models.ImageField(upload_to=order_image_path, null=True, blank=True)
    original_file_name = models.CharField(max_length=255, null=True, blank=True)
    is_mockup = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for Order {self.order.order_number}"


