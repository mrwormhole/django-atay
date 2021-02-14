from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from .forms import *
import json

def store(request):
    categories = Category.objects.all()
    categoryImages = {}
    for i in categories:
        categoryImages[i.name] = CategoryImage.objects.get(category=i).resized_image.url
    
    latest_arrived_products = Product.objects.filter(discounted_price = None).order_by("-date_added")[:8]
    on_sale_products = Product.objects.exclude(discounted_price = None)[:8]
    
    productThumbnails = {}
    for i in latest_arrived_products | on_sale_products:
        qs = ProductThumbnail.objects.filter(product = i)
        if len(qs) < 2:
            return HttpResponse(f'<h1>Server Error! There should be at least 2 product thumbnails for a product! ({i.name})</h1>')
        productThumbnails[i.id] = [0,0]
        productThumbnails[i.id][0] = qs[0].resized_image.url
        productThumbnails[i.id][1] = qs[1].resized_image.url

    productWislistStatuses = {}
    if request.user.is_authenticated:
        customer = request.user.customer
        for i in latest_arrived_products | on_sale_products:
            qs = Wishlist.objects.filter(customer = customer, product = i)
            if len(qs) == 1:
                productWislistStatuses[i.id] = True
            elif len(qs) == 0:
                productWislistStatuses[i.id] = False   

    context = {"categories": categories, 
               "categoryImages": categoryImages, 
               "onSaleProducts": on_sale_products,  
               "latestArrivedProducts": latest_arrived_products, 
               "productThumbnails": productThumbnails,
               "productWishlistStatuses": productWislistStatuses}
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
    text = request.GET.get('search')
    products = {}
    if text is not None and text != "":
        vector = SearchVector("name", weight="A") + SearchVector("description", weight="B") + SearchVector("brand", weight="B")
        query = SearchQuery(text)
        ''' Full text search on products name and description, and product should be in the stock '''
        products = Product.objects.annotate(rank = SearchRank(vector, query)).filter(Q(rank__gte=0.2) & Q(stock__gte=1)).order_by('-rank')
        #print(products.values_list('name', 'rank'))
    context = {"products": products}
    return render(request, "store/catalog.html", context)

def product(request, id):
    product = get_object_or_404(Product, pk=id)
    qs = product.images.all()
    if len(qs) < 2:
        return HttpResponse(f'<h1>Server Error! There should be at least 2 product images for a product! ({product.name})</h1>')

    product = Product.objects.get(id = id)
    customer = request.user.customer
    wishlist = Wishlist.objects.filter(customer = customer, product= product)
    productWishlisted = False
    if len(wishlist) > 0:
        productWishlisted = True

    context = {"product": product, "productImages": qs, "productWishlisted": productWishlisted}
    return render(request, "store/product.html", context)

def signup(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:login')
    else:
        form = UserSignUpForm()
    return render(request, "store/signup.html", {'form': form})

@login_required
def account(request):
    customer = request.user.customer
    orders = Order.objects.filter(Q(transaction_id__isnull=False) & Q(customer=customer)).order_by("-date_ordered")
    orders_with_order_items = []

    for i,o in enumerate(orders, start=0):
        order_items = o.order_items.all()
        orders_with_order_items.append([0, 0])
        status = 'PAID' if o.status == "P" else 'DELIVERED'
        total_price = '£' + str(o.get_cart_total_price())
        orders_with_order_items[i][0] = (i+1, o.date_ordered.date(), o.transaction_id, status, total_price)
        orders_with_order_items[i][1] = order_items

    should_show = "show"
    if len(orders) > 5:
        should_show = ""
    welcome_with_full_name = f'Welcome back {customer.full_name}!'

    # print(orders_with_order_items)
    context = {"orders_with_order_items": orders_with_order_items, "should_show": should_show, "welcome_with_full_name": welcome_with_full_name}
    return render(request, "store/account.html", context)

@login_required
def wishlist(request):
    customer = request.user.customer
    wishlist = Wishlist.objects.filter(customer = customer)
    products = [w.product for w in wishlist]
    
    productThumbnails = {}
    for i in products:
        qs = ProductThumbnail.objects.filter(product = i)
        if len(qs) < 1:
            return HttpResponse(f'<h1>Server Error! There should be at least 1 product thumbnail for a product! ({i.name})</h1>')
        productThumbnails[i.id] = qs[0].resized_image.url

    context = {"products": products, "productThumbnails": productThumbnails}
    return render(request, "store/wishlist.html", context)

@login_required
def wishlistAdd(request):
    if request.method == 'POST':
        productID = json.loads(request.body)["productID"]
        product = Product.objects.get(id = productID)
        customer = request.user.customer
        wishlist = Wishlist.objects.filter(customer = customer, product= product)
        if len(wishlist) == 0:
            Wishlist.objects.create(customer=customer, product=product)
            print(wishlist)
            return JsonResponse({"status" : "operation succeeded"})

    return JsonResponse({"status" : "API doesn't work that way"})

@login_required
def wishlistRemove(request):
    if request.method == 'DELETE':
        productID = json.loads(request.body)["productID"]
        product = Product.objects.get(id = productID)
        customer = request.user.customer
        wishlist = Wishlist.objects.filter(customer = customer, product= product)
        if len(wishlist) == 1:
            wishlist.delete()
            return JsonResponse({"status" : "operation succeeded"})

    return JsonResponse({"status" : "API doesn't work that way"})

