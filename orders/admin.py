from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('item_type', 'dimension', 'map_file', 'weight', 'price')
    # Removed readonly to allow editing for Maps

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'current_total_price')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    readonly_fields = ('current_total_price',)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
