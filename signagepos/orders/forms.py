from django import forms
from .models import Order, OrderImage
from accounts.models import CustomUser

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['created_on']
        fields = [
            'width', 'height', 'color', 'design_notes', 'cut_type', 'is_business',
            'order_number', 'shipping_address', 'city', 'state', 'zip_code',
            'quantity', 'deposit', 'price', 'order_status', 'tracking_number',
            'company_notes', 'acrylic_cost', 'silicone_cost',
            'silicone_amount_meters', 'led_light_cost', 'led_light_meters',
            'power_supply_cost', 'mounting_accessories_cost', 'created_on', 'warranty_start_date', 'warranty_duration', 'other_expenses'
        ]
         
       

        # Customize form fields using widgets or add additional fields if needed
        widgets = {
        'width': forms.NumberInput(attrs={'class': 'form-control'}),
        'height': forms.NumberInput(attrs={'class': 'form-control'}),
        'color': forms.Select(attrs={'class': 'form-control'}),
        'design_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        'cut_type': forms.Select(attrs={'class': 'form-control'}),
        'is_business': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'order_number': forms.TextInput(attrs={'class': 'form-control'}),
        'shipping_address': forms.TextInput(attrs={'class': 'form-control'}),
        'city': forms.TextInput(attrs={'class': 'form-control'}),
        'state': forms.TextInput(attrs={'class': 'form-control'}),
        'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        'deposit': forms.NumberInput(attrs={'class': 'form-control'}),
        'price': forms.NumberInput(attrs={'class': 'form-control'}),
        'order_status': forms.Select(attrs={'class': 'form-control'}),
        'tracking_number': forms.TextInput(attrs={'class': 'form-control'}),
        'company_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        'acrylic_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        'silicone_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        'silicone_amount_meters': forms.NumberInput(attrs={'class': 'form-control'}),
        'led_light_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        'led_light_meters': forms.NumberInput(attrs={'class': 'form-control'}),
        'power_supply_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        'mounting_accessories_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        'warranty_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        'warranty_duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Months'}),
        'other_expenses': forms.NumberInput(attrs={'class': 'form-control'}),
        

        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['image'].required = False  # Make the image field optional
            self.fields['is_business'].required = False
            self.fields['warranty_start_date'].required = False
            self.fields['warranty_duration'].required = False
            

        def clean_warranty_duration(self):
            # Convert an empty string to None for DurationField
            warranty_duration = self.cleaned_data.get('warranty_duration')
            if warranty_duration == '':
                return None
            return warranty_duration

class CustomerForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name' , 'phone_number']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

        


class OrderImagesForm(forms.ModelForm):
    class Meta:
        model = OrderImage
        fields = ['order_images']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['image'].required = False  # Make the image field optional
        # widgets = {
        #     'order_images': forms.ClearableFileInput(attrs={'multiple': True}),
        # }