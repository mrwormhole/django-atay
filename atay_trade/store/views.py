from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
# from django.contrib import messages
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from .forms import *

def store(request):
    categories = Category.objects.all()
    categoryImages = {}
    for i in categories:
        categoryImages[i.name] = CategoryImage.objects.get(category=i).resized_image.url
    
    products = Product.objects.all()
    productThumbnails = {}
    for i in products:
        qs = ProductThumbnail.objects.filter(product = i)
        if len(qs) < 2:
            return HttpResponse(f'<h1>Server Error! There should be at least 2 product thumbnails for a product! ({i.name})</h1>')
        productThumbnails[i.name] = [0,0]
        productThumbnails[i.name][0] = qs[0].resized_image.url
        productThumbnails[i.name][1] = qs[1].resized_image.url

    context = {"categories": categories, "categoryImages": categoryImages, "products": products, "productThumbnails": productThumbnails}
    return render(request, "store/index.html", context)

class CartList(APIView):

    def get(self, request, format=None):
        if request.user.is_authenticated == False:
            return Response({}, status=status.HTTP_200_OK)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, status=Order.NOT_PAID_STATUS)
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
        order, created = Order.objects.get_or_create(customer = customer, status=Order.NOT_PAID_STATUS)
        orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)
        orderItem.quantity = orderItem.quantity + 1
        orderItem.save()
        
        serializer = OrderSerializer(order)
        serializer_data = serializer.data
        return Response(serializer_data, status=status.HTTP_200_OK)

class CartRemove(APIView):

    def delete(self, request, format=None):
        productID = request.data["productID"]
        product = Product.objects.get(id = productID)

        if request.user.is_authenticated == False:
            return Response({}, status=status.HTTP_200_OK)
        
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, status=Order.NOT_PAID_STATUS)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        orderItem.delete()

        serializer = OrderSerializer(order)
        serializer_data = serializer.data
        return Response(serializer.data, status=status.HTTP_200_OK)
        
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, status=Order.NOT_PAID_STATUS)
        order_items = order.order_items.all()
        order_total = {'total_price': order.get_cart_total_price(), 'items_count': order.get_cart_items_count()}
    else:
        order_items = []
        order_total = {'total_price': 0, 'items_count' : 0}

    context = {'items': order_items, 'total' : order_total }
    return render(request, "store/checkout.html", context)

def contact(request):
    context = {}
    return render(request, "store/contact.html", context)

def catalog(request):
    text = request.GET.get('q')
    if text is not None and text != "":
        vector = SearchVector("name", weight="A") + SearchVector("description", weight="B") + SearchVector("brand", weight="B")
        query = SearchQuery(text)
        ''' Full text search on products name and description, and product should be in the stock '''
        products = Product.objects.annotate(rank = SearchRank(vector, query)).filter(Q(rank__gte=0.2) & Q(stock__gte=1)).order_by('-rank')
        # print(products.values_list('name', 'rank'))
    context = {}
    return render(request, "store/catalog.html", context)

def product(request, id):
    product = get_object_or_404(Product, pk=id)
    qs = product.images.all()
    if len(qs) < 2:
        return HttpResponse(f'<h1>Server Error! There should be at least 2 product images for a product! ({product.name})</h1>')
    context = {"product": product, "productImages": qs}
    return render(request, "store/product.html", context)

def signup(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get('username')
            # messages.success(request, f'Account created for {username}!')
            return redirect('store:login')
    else:
        form = UserSignUpForm()
    return render(request, 'store/signup.html', {'form': form})

@login_required
def account(request):
    context = {}
    return render(request, 'store/account.html', context)
