from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, reverse
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
import datetime
import hashlib

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
            try:
                cart = json.loads(request.COOKIES["cart"])
            except:
                cart = {}
            dictResponse = {"total_price": 0, "items_count": 0, "order_items" : [], "delivery_price": 0}

            for i in cart:
                try:
                    product = Product.objects.get(id=i)
                    productImages = product.images.all()
                    dictResponse["order_items"].append({
                        "product": {
                            "id": product.id,
                            "name": product.name,
                            "price": product.price,
                            "discounted_price": product.discounted_price,
                            "model_number": product.model_number,
                            "images": [
                                { "image": productImages[0].image.url }
                            ],
                        }, 
                        "quantity": cart[i]["quantity"],
                    })
                    dictResponse["items_count"] += cart[i]["quantity"]
                    if product.discounted_price is None:
                        dictResponse["total_price"] += round(product.price * cart[i]["quantity"], 2)
                    else:
                        dictResponse["total_price"] += round(product.discounted_price * cart[i]["quantity"], 2)
                    
                except Exception as e:
                    print("EXCEPTION OCCURED", e)
                    continue
            
            dictResponse["delivery_price"] = Order.get_delivery_price(dictResponse["total_price"])
            dictResponse["subtotal"] = dictResponse["total_price"] 
            dictResponse["total_price"] = dictResponse["delivery_price"] + dictResponse["subtotal"]
            return Response(dictResponse, status=status.HTTP_200_OK)

        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, status=Order.NOT_PAID_STATUS)
        serializer = OrderSerializer(order)
        serializer_data = serializer.data
        return Response(serializer_data, status=status.HTTP_200_OK)

class CartAdd(APIView):

    def post(self, request, format=None):
        if request.user.is_authenticated == False:
            return Response({}, status=status.HTTP_200_OK)

        productID = request.data["productID"]
        product = Product.objects.get(id = productID)

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
        if request.user.is_authenticated == False:
            return Response({}, status=status.HTTP_200_OK)

        productID = request.data["productID"]
        product = Product.objects.get(id = productID)

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
        order_total = {'total_price': order.get_cart_total_price(), 
                       'items_count': order.get_cart_items_count(), 
                       "delivery_price": Order.get_delivery_price(order.get_cart_subtotal_price()),
                       "subtotal" : order.get_cart_subtotal_price()}
        customer = {'first_name': request.user.first_name, 'last_name': request.user.last_name, 'email' : request.user.email}
        context = {'items': order_items, 'total' : order_total, 'customer': customer}
    else:
        context = {}

    result = processOrderForm(request)
    if "error" in result:
        context["error"] = result["error"]
    if "success" in result:
        context["success"] = result["success"]
        response = render(request, "store/checkout.html", context)
        response.delete_cookie("cart")
        return response
    
    return render(request, "store/checkout.html", context)

def contact(request):
    context = {}
    return render(request, "store/contact.html", context)

def catalog(request, category = None):
    page = request.GET.get("page")
    text = request.GET.get("search")
    sortBy = request.GET.get("sortBy")
    priceRange = request.GET.get("priceRange")
    maxPrice = 0
    minPrice = 0  

    categories = Category.objects.all()
    products = []
    if text is not None and text != "":
        vector = SearchVector("name", weight="A") + SearchVector("description", weight="B") + SearchVector("brand", weight="B")
        query = SearchQuery(text)
        ''' Full text search on products name and description, and product should be in the stock '''
        products = Product.objects.annotate(rank = SearchRank(vector, query)).filter(Q(rank__gte=0.2) & Q(stock__gte=1)).order_by('-rank')
        #print(products.values_list('name', 'rank'))
    else:
        if sortBy == "sale":
            products = Product.objects.exclude(Q(discounted_price=None) & ~Q(stock=0)).order_by("-discounted_price")
        elif sortBy == "toLowerPrice":
            products = Product.objects.filter(Q(stock__gte = 1)).order_by("-price")
        elif sortBy == "toHigherPrice":
            products = Product.objects.filter(Q(stock__gte = 1)).order_by("price")
        else:
            products = Product.objects.filter(Q(stock__gte = 1)).order_by("-date_added")


    if priceRange is not None:
        prices = priceRange.split("-")
        minPrice = float(prices[0])
        maxPrice = float(prices[1])
        products = Product.objects.filter(Q(stock__gte = 1) & Q(price__gte = minPrice) & Q(price__lte=maxPrice)).order_by("price")
        sortBy = "toLowerPrice"

    productThumbnails = {}
    for p in products:
        qs = ProductThumbnail.objects.filter(product = p)
        if len(qs) < 2:
            return HttpResponse(f'<h1>Server Error! There should be at least 2 product thumbnails for a product! ({p.name})</h1>')
        productThumbnails[p.id] = [0,0]
        productThumbnails[p.id][0] = qs[0].resized_image.url
        productThumbnails[p.id][1] = qs[1].resized_image.url

    productWislistStatuses = {}
    if request.user.is_authenticated:
        customer = request.user.customer
        for p in products:
            qs = Wishlist.objects.filter(customer = customer, product = p)
            if len(qs) == 1:
                productWislistStatuses[p.id] = True
            elif len(qs) == 0:
                productWislistStatuses[p.id] = False 

    categoryName = None
    if category is not None and category != "":
        categoryName = category
        products = products.filter(Q(category__name__icontains = category))

    paginator = Paginator(products, 6)
    products = paginator.get_page(page)
    #print(products.object_list)
    
    context = {"categories": categories,
               "products": products, 
               "productThumbnails": productThumbnails, 
               "productWishlistStatuses": productWislistStatuses, 
               "sortBy": sortBy, 
               "minPrice": minPrice,
               "maxPrice": maxPrice,
               "categoryName": categoryName}
    return render(request, "store/catalog.html", context)

def product(request, id):
    product = get_object_or_404(Product, pk=id)
    qs = product.images.all()
    if len(qs) < 2:
        return HttpResponse(f'<h1>Server Error! There should be at least 2 product images for a product! ({product.name})</h1>')

    product = Product.objects.get(id = id)
    wishlist = []
    if request.user.is_authenticated:
        customer = request.user.customer
        wishlist = Wishlist.objects.filter(customer = customer, product= product)

    productWishlisted = False
    if len(wishlist) > 0:
        productWishlisted = True

    context = {"product": product, "productImages": qs, "productWishlisted": productWishlisted}
    return render(request, "store/product.html", context)

def signup(request):
    if request.user.is_authenticated:
        print("test")
        return redirect("store:account")

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
        if o.status == "P":
            status = 'PAID'
        else:
            status = 'DELIVERED'
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

# TODO this is not a view, move to a proper file maybe? not forms.py and not utils.py, this seems like sort of validators.py
def processOrderForm(request):
    if request.method == "POST":
        customer_first_name = request.POST.get("first_name")
        customer_last_name = request.POST.get("last_name")
        customer_email = request.POST.get("email_address")
        customer_country = request.POST.get("country")
        customer_address = request.POST.get("street_address")
        customer_postcode = request.POST.get("postcode")
        customer_city = request.POST.get("city")
        customer_phone_number = request.POST.get("phone_number")
        customer_total = request.POST.get("total_price") # this is not trusted
        print("customer total", customer_total)

        if customer_first_name is None or customer_first_name.replace(" ", "") == "":
            return {"error": "First name can not be empty!"}
        if customer_last_name is None or customer_last_name.replace(" ", "") == "":
            return {"error": "Last name can not be empty!"}
        if customer_email is None or customer_email.replace(" ", "") == "":
            return {"error": "Email can not be empty!"}
        if customer_country is None or customer_country.replace(" ", "") == "":
            return {"error": "Country can not be empty!"}
        if customer_address is None or customer_address.replace(" ", "") == "":
            return {"error": "Address can not be empty!"}
        if customer_postcode is None or customer_address.replace(" ","") == "":
            return {"error": "Postcode can not be empty!"}
        if customer_city is None or customer_city.replace(" ","") == "":
            return {"error": "City can not be empty!"}
        if customer_phone_number is None or customer_phone_number.replace(" ","") == "":
            return {"error": "Phone number can not be empty!"}        
        if customer_total is None or customer_total.replace(" ", "") == "" or float(customer_total) == 0:
            return {"error": "Your cart can not be empty!"}

        customer_full_name = str(customer_first_name) + " " + str(customer_last_name)

        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer = customer, status=Order.NOT_PAID_STATUS)
        else:
            try:
                cart = json.loads(request.COOKIES["cart"])
            except Exception as e:
                print("EXCEPTION OCCURED", e)
                return {"error": e}
            dictCart = {"total_price": 0, "items_count": 0, "order_items" : [], "delivery_price": 0}
            for i in cart:
                try:
                    product = Product.objects.get(id=i)
                    productImages = product.images.all()
                    dictCart["order_items"].append({
                        "product": {
                            "id": product.id,
                            "name": product.name,
                            "price": product.price,
                            "discounted_price": product.discounted_price,
                            "model_number": product.model_number,
                            "images": [
                                { "image": productImages[0].image.url }
                            ],
                        }, 
                        "quantity": cart[i]["quantity"],
                    })
                    dictCart["items_count"] += cart[i]["quantity"]
                    if product.discounted_price is None:
                        dictCart["total_price"] += round(product.price * cart[i]["quantity"], 2)
                    else:
                        dictCart["total_price"] += round(product.discounted_price * cart[i]["quantity"], 2)
                    
                except Exception as e:
                    print("EXCEPTION OCCURED", e)
                    return {"error": e}
                
                dictCart["delivery_price"] = Order.get_delivery_price(dictCart["total_price"])
                dictCart["subtotal"] = dictCart["total_price"] 
                dictCart["total_price"] += dictCart["delivery_price"]
            
            customer, created = Customer.objects.get_or_create(full_name=customer_full_name, guest_email = customer_email)
            customer.save()
            order = Order.objects.create(customer=customer, status=Order.NOT_PAID_STATUS)
            
            try:
                for d in dictCart["order_items"]:
                    product = Product.objects.get(id=d["product"]["id"])
                    orderItem = OrderItem.objects.create(product=product, order=order, quantity=int(d["quantity"]))
            except Exception as e:
                print("EXCEPTION OCCURED", e)
                return {"error": e}

        transaction_key = str(datetime.datetime.now().timestamp()) + customer_full_name + customer_email
        digest = hashlib.sha256(transaction_key.encode('utf-8')).hexdigest()
        transaction_id = digest
        order.transaction_id = transaction_id

        print("YOUR ACTUAL TOTAL", float(order.get_cart_total_price()))
        if float(customer_total) == float(order.get_cart_total_price()):
            order.status = Order.PAID_STATUS
            ShippingAddress.objects.create(customer=customer, 
                                           order=order, 
                                           address= customer_address, 
                                           city= customer_city,
                                           country= customer_country,
                                           postcode= customer_postcode,
                                           phone_number= customer_phone_number)
            try:
                if request.user.is_authenticated:
                    order_items = order.order_items.all()
                    for oi in order_items:
                        product = Product.objects.get(id=oi.product.id)
                        product.stock -= oi.quantity
                        product.save(update_fields=["stock"])
                else:
                    for d in dictCart["order_items"]:
                        product = Product.objects.get(id=d["product"]["id"])
                        product.stock -= int(d["quantity"])
                        product.save(update_fields=['stock'])
            except:
                return {"error": "Something went wrong during the payment process!"}
        else:
            return {"error": "Your payment has been rejected!"}

        order.save()
        return {"success": "You have successfully placed your order. Thanks for your purchase!"}

    return {"error": None}
    

