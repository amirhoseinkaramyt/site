from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from .forms import OrderItemForm, OrderReceiptForm

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_create(request):
    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        return redirect('order_detail', order_id=order.id)
    # If accessed via GET, render a simple page or redirect.
    # For simplicity, render a page with a button.
    return render(request, 'orders/order_create.html')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    item_form = OrderItemForm()
    receipt_form = OrderReceiptForm(instance=order)

    if request.method == 'POST':
        if 'add_item' in request.POST:
            # Check if order status allows adding items?
            # Usually users can add items only if not completed/paid.
            if order.status not in ['PENDING_PRICE', 'AWAITING_PAYMENT']:
                 return redirect('order_detail', order_id=order.id)

            item_form = OrderItemForm(request.POST, request.FILES)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.order = order
                item.save()
                return redirect('order_detail', order_id=order.id)

        elif 'upload_receipt' in request.POST:
            receipt_form = OrderReceiptForm(request.POST, request.FILES, instance=order)
            if receipt_form.is_valid():
                order = receipt_form.save(commit=False)
                order.status = 'PAYMENT_UPLOADED'
                order.save()
                return redirect('order_detail', order_id=order.id)

        elif 'delete_item' in request.POST:
             item_id = request.POST.get('item_id')
             item = get_object_or_404(OrderItem, id=item_id, order=order)
             item.delete()
             return redirect('order_detail', order_id=order.id)

    context = {
        'order': order,
        'item_form': item_form,
        'receipt_form': receipt_form,
    }
    return render(request, 'orders/order_detail.html', context)
