from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *

admin.site.site_header = "Atay Admin"
admin.site.site_title = "Atay Admin Area"
admin.site.index_title = "Welcome to Atay Admin Area"
admin.site.unregister(Group)
admin.site.register(CustomUser)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
 list_display = ('customer', 'status', 'date_ordered', 'transaction_id',)
 list_filter = ('status', 'date_ordered',)
 search_fields = ('customer__user__email', 'customer__full_name','transaction_id',)
 date_hierarchy = 'date_ordered'
 ordering = ('status', 'date_ordered',)

admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Wishlist)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductThumbnailInline(admin.TabularInline):
    model = ProductThumbnail
    max_num = 2

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ ProductThumbnailInline, ProductImageInline, ] 
    list_display = ("name", "price", "discounted_price", "brand", "model_number", "stock",)
    list_filter = ('category__name', 'brand','date_added',)
    search_fields = ('name', 'brand','model_number',)
    date_hierarchy = 'date_added'
    ordering = ('stock', 'date_added',)
    actions = ["discount_10", "discount_20", "discount_30", "discount_40", "discount_50", "close_discount",]

    def discount(self, request, queryset, sale_percentage):
        for product in queryset:
            """ Set a discount of selected products """
            multiplier = round(sale_percentage / 100.0, 2)
            old_price = product.price
            discounted_price = round(old_price - (old_price * multiplier), 2)
            product.discounted_price = discounted_price
            product.save(update_fields=['discounted_price'])

    def discount_10(self, request, queryset):
        self.discount(request, queryset, 10)

    def discount_20(self, request, queryset):
        self.discount(request, queryset, 20)
    
    def discount_30(self, request, queryset):
        self.discount(request, queryset, 30)

    def discount_40(self, request, queryset):
        self.discount(request, queryset, 40)

    def discount_50(self, request, queryset):
        self.discount(request, queryset, 50)

    def close_discount(self, request, queryset):
        queryset.update(discounted_price = None) # this is better than looping through all objects in queryset and calling .save()

    discount_10.short_description = "Set 10%% discount"
    discount_20.short_description = "Set 20%% discount"
    discount_30.short_description = "Set 30%% discount"
    discount_40.short_description = "Set 40%% discount"
    discount_50.short_description = "Set 50%% discount"
    close_discount.short_description = "Close discount"

class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    max_num = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ CategoryImageInline, ] 
