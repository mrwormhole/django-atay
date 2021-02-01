from .models import Order, OrderItem, Product, ProductImage, ProductThumbnail
from rest_framework import serializers

class ProductThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductThumbnail
        fields = ["image"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]

class ProductSerializer(serializers.ModelSerializer):
    thumbnails = ProductThumbnailSerializer(many = True, read_only= True)
    images = ProductImageSerializer(many = True, read_only = True)
    class Meta:
        model = Product
        fields = ["id", "category", "name", "price", "discounted_price", "model_number", "date_added", "stock", "description", "images", "thumbnails"]

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False, read_only = True)
    class Meta:
        model = OrderItem
        fields = ["product", "order", "quantity", "date_added", "product"]

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ["customer", "total_price", "items_count", "date_ordered", "complete", "transaction_id", "order_items"]
    
    def get_total_price(self, obj):
        return obj.get_cart_total_price
    
    def get_items_count(self, obj):
        return obj.get_cart_items_count