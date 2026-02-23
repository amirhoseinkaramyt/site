from django import forms
from .models import Order, OrderItem

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['item_type', 'dimension', 'map_file']
        widgets = {
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'dimension': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Dimension (mm)'}),
            'map_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        item_type = cleaned_data.get('item_type')
        dimension = cleaned_data.get('dimension')
        map_file = cleaned_data.get('map_file')

        if item_type in ['CIRCLE', 'SQUARE'] and not dimension:
            raise forms.ValidationError("Dimension is required for Circle/Square.")
        if item_type == 'MAP' and not map_file:
            raise forms.ValidationError("Map file is required for Map items.")
        return cleaned_data

class OrderReceiptForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['receipt']
        widgets = {
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
        }
