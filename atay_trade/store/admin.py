from django.contrib import admin
from .models import *

admin.site.site_header = "Atay Admin"
admin.site.site_title = "Atay Admin Area"
admin.site.index_title = "Welcome to Atay Admin Area"

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductAdmin(admin.ModelAdmin):
    inlines = [ ProductImageInline ]

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
