from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import *
from .serializers import *
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

def store(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "store/index.html", context)

'''
# TODO remove this from views and use DRF if possible to solve this issue
def cart(request):
    itemsResponse =[]
    # return list of items where item has a value for product image URL, product name, product price, item quantity
    if request.user.is_authenticated and request.method == "GET":
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_items = order.orderitem_set.all()
        for q in order_items:
            itemsResponse.append({"productName": q.product.name, "productPrice" : q.product.price, "quantity": q.quantity})
        print(order_items)

    return JsonResponse({"cart": itemsResponse})
'''

class CartList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        serializer = OrderSerializer(order)
        serializer_data = serializer.data
        return Response(serializer.data)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_items = order.order_items.all()
        order_total = {'total_price': order.get_cart_total_price, 'items_count': order.get_cart_items_count}
    else:
        order_items = []
        order_total = {'total_price': 0, 'items_count' : 0}

    context = {'items': order_items, 'total' : order_total }
    return render(request, "store/checkout.html", context)

def contact(request):
    context = {}
    return render(request, "store/contact.html", context)

def catalog(request):
    context = {}
    return render(request, "store/catalog.html", context)

def product(request, id):
    product = get_object_or_404(Product, pk=id)
    print(product)
    context = {"product": product}
    return render(request, "store/product.html", context)
