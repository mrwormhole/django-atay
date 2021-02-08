from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, SmartResize
from datetime import datetime
import pytz

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.email

class Category(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

def upload_to(folder_name):
    now = datetime.now(pytz.utc)
    return f"{folder_name}/{now:%Y/%m}/"

class CategoryImage(models.Model):
    # category images size has to be 800x533 (kinda like horizontal wide square)
    category = models.OneToOneField(Category, related_name="image", on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=upload_to("category_images") ,null=True, blank=True)
    resized_image = ImageSpecField(source="image", processors=[ResizeToFill(800,533)], format="JPEG", options={"quality": 80}) 

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=100, null=True)
    price = models.FloatField()
    discounted_price = models.FloatField(null=True, blank=True)
    model_number = models.CharField(max_length=100, null=True, unique=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    stock = models.IntegerField(default=0, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name + " " + str(self.model_number)

    def calculate_sale_percantage_number(self):
        sale_percentage = round((self.price - self.discounted_price) / self.price, 2)
        return sale_percentage * 100

class Wishlist(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class ProductImage(models.Model):
    # product images size has to be 1000 x 972 (kinda like horizontal wide square)
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=upload_to("product_images") ,null=True, blank=True)
    resized_image = ImageSpecField(source="image", processors=[SmartResize(1000,972)], format="JPEG", options={"quality": 80}) 

class ProductThumbnail(models.Model):
    # product thumbnails size has to be 1000 x 1364 (kinda like vertical wide rectangle)
    product = models.ForeignKey(Product, related_name="thumbnails", on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=upload_to("product_thumbnails") , null=True, blank=True)
    resized_image = ImageSpecField(source="image", processors=[ResizeToFill(1000,1364)], format="JPEG", options={"quality": 80})

class Order(models.Model):
    NOT_PAID_STATUS = 'NP'
    PAID_STATUS = 'P'
    DELIVERED_STATUS = 'D'

    STATUS_CHOICES = (
        (NOT_PAID_STATUS, 'Not paid'),
        (PAID_STATUS, 'Paid'),
        (DELIVERED_STATUS, 'Delivered')
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, null=True, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=NOT_PAID_STATUS, null=False, blank=False)

    def __str__(self):
        return str(self.customer.user.email + f" (status: {self.status})")

    def get_cart_total_price(self):
        orderitems = self.order_items.all()
        return round(sum([item.get_total() for item in orderitems]), 2)
    
    def get_cart_items_count(self):
        orderitems = self.order_items.all()
        return sum([item.quantity for item in orderitems])

    def get_delivery_price(self):
        ''' Free delivery over 200 pounds, 5 pounds delivery fee under 200 pounds '''
        return 0 if self.get_cart_total_price() > 200 else 5
    
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
    product = models.OneToOneField(Product, on_delete=models.PROTECT, null=True, blank=True)
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.order.customer is None:
            return str(str(self.quantity) + " X " + self.product.name + " by AnonymousUser")
        else:
            return str(str(self.quantity) + " X " + self.product.name + " by "+(self.order.customer.name))

    def get_total(self):
        return round(self.product.price * self.quantity, 2)

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    zipcode = models.CharField(max_length=10, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    first_name = None
    last_name = None
    username = None
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email