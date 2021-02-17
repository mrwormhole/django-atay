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
    list_display = ('user', 'full_name', 'guest_email')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'status', 'date_ordered', 'transaction_id', 'total_price')
    readonly_fields = ('total_price', 'customer_name')
    list_filter = ('status', 'date_ordered',)
    search_fields = ('customer__user__email', 'customer__full_name','transaction_id',)
    date_hierarchy = 'date_ordered'
    ordering = ('status', '-date_ordered',)
    actions = ["set_unpaid", "set_paid", "set_delivered",]

    def total_price(self, obj):
            return "£" + str(obj.get_cart_total_price())
    
    def customer_name(self, obj):
        if obj.customer.guest_email is None:
            return str(obj.customer.full_name) + " (NOT GUEST)"
        else:
            return str(obj.customer.full_name) + " (GUEST)"

    def set_status(self, request, queryset, status):
            for order in queryset:
                """ Set a status of selected orders """
                order.status = status
                order.save(update_fields=['status'])

    def set_unpaid(self, request, queryset):
        self.set_status(request, queryset, Order.NOT_PAID_STATUS)
    
    def set_paid(self, request, queryset):
        self.set_status(request, queryset, Order.PAID_STATUS)

    def set_delivered(self, request, queryset):
        self.set_status(request, queryset, Order.DELIVERED_STATUS)
    
    set_unpaid.short_description = "Set order to unpaid"
    set_paid.short_description = "Set order to paid"
    set_delivered.short_description = "Set order to delivered"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'date_added', )
    list_filter = ('date_added',)
    search_fields = ('product__name', 'order__transaction_id', )
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'customer_name', 'postcode', 'phone_number', 'country', 'date_added')
    readonly_fields = ('customer_name', )
    list_filter = ('date_added', 'country')
    search_fields = ('order__transaction_id', 'postcode','country', 'phone_number')
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)

    def customer_name(self, obj):
        if obj.customer.guest_email is None:
            return str(obj.customer.full_name) + " (NOT GUEST)"
        else:
            return str(obj.customer.full_name) + " (GUEST)"

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'date_added',)
    list_filter = ('date_added',)
    search_fields = ('customer__user__email', 'product__name',)
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)

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
