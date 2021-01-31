from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *


def store(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "store/index.html", context)


class CartList(APIView):

    def get(self, request, format=None):
        if request.user.is_authenticated == False:
            return Response({}, status=status.HTTP_200_OK)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        serializer = OrderSerializer(order)
        serializer_data = serializer.data
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartAdd(APIView):

    def post(self, request, format=None):
        productID = request.data["productID"]
        product = Product.objects.get(id = productID)

        if request.user.is_authenticated == False:
            return Response({}, status=status.HTTP_200_OK)
        
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)
        orderItem.quantity = orderItem.quantity + 1
        orderItem.save()
        
        serializer = OrderSerializer(order)
        serializer_data = serializer.data
        return Response(serializer_data, status=status.HTTP_200_OK)

        
class CartRemove(APIView):

    def delete(self, request, format=None):
        product = Product.objects.get(id = request.data["id"])

        if request.user.is_authenticated == False:
            return Response({}, status=status.HTTP_200_OK)
        
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        orderItem.delete()

        serializer = OrderSerializer(order)
        serializer_data = serializer.data
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
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
    productImages = product.images.all()
    context = {"product": product, "productImages": productImages}
    return render(request, "store/product.html", context)
