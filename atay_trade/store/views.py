from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import *

def store(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "store/index.html", context)

# TODO remove this from views and use DRF if possible to solve this issue
def cart(request):
    itemsResponse =[]
    # return list of items where item has a value for product image URL, product name, product price, item quantity
    if request.user.is_authenticated and request.method == "GET":
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_items = order.orderitem_set.all()
        for q in order_items:
            # TODO add image URL(thumbnail image) here
            itemsResponse.append({"productName": q.product.name, "productPrice" : q.product.price, "quantity": q.quantity})
        print(order_items)

    return JsonResponse({"cart": itemsResponse})

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_items = order.orderitem_set.all()
        order_total = {'total_price': order.get_cart_total, 'total_items': order.get_cart_items_count}
    else:
        order_items = []
        order_total = {'total_price': 0, 'total_items' : 0}

    context = {'items': order_items, 'total' : order_total }
    return render(request, "store/checkout.html", context)

def contact(request):
    context = {}
    return render(request, "store/contact.html", context)

def catalog(request):
    context = {}
    return render(request, "store/catalog.html", context)

def product(request):
    context = {}
    return render(request, "store/product.html", context)
