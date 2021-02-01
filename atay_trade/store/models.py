from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeCanvas
from datetime import datetime
import pytz

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, null=True)
    price = models.FloatField()
    discounted_price = models.FloatField(null=True, blank=True)
    model_number = models.CharField(max_length=100, null=True, unique=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    stock = models.IntegerField(default=0, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    #TODO: wishlist is designed for db but not added yet

    def __str__(self):
        return self.name + " " + str(self.model_number)

    @property
    def calculate_sale_percantage_number(self):
        sale_percentage = round((self.price - self.discounted_price) / self.price, 2)
        return sale_percentage * 100

def upload_to(folder_name):
    now = datetime.now(pytz.utc)
    return f"{folder_name}/{now:%Y/%m}/"

class ProductImage(models.Model):
    # product images size has to be 1000 x 972 (kinda like horizontal wide square)
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=upload_to("product_images") ,null=True, blank=True)
    resized_image = ImageSpecField(source="image", processors=[ResizeCanvas(1000,972)], format="JPEG", options={"quality": 80}) 

class ProductThumbnail(models.Model):
    # product thumbnails size has to be 1000 x 1364 (kinda like vertical wide rectangle)
    product = models.ForeignKey(Product, related_name="thumbnails", on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=upload_to("product_thumbnails") , null=True, blank=True)
    resized_image = ImageSpecField(source="image", processors=[ResizeCanvas(1000,1364)], format="JPEG", options={"quality": 80})

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=100, null=True, unique=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total_price(self):
        orderitems = self.order_items.all()
        return round(sum([item.get_total for item in orderitems]), 2)
    
    @property
    def get_cart_items_count(self):
        orderitems = self.order_items.all()
        return sum([item.quantity for item in orderitems])
    
    @property
    def get_availability_from_stock(self):
        is_available_in_stock = True
        products_that_are_not_available = []
        orderitems = self.order_items.all()
        for oi in orderitems:
            if oi.product.stock < oi.quantity:
                is_available_in_stock = False
                products_that_are_not_available.append(oi.product)
        return is_available_in_stock, products_that_are_not_available   

class OrderItem(models.Model):
    product = models.OneToOneField(Product, on_delete=models.SET_NULL, null=True, blank=True) #dont like this reverse shit
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return round(self.product.price * self.quantity, 2)

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    zipcode = models.CharField(max_length=10, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address