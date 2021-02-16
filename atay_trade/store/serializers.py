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
    images = ProductImageSerializer(many = True, read_only = True)
    class Meta:
        model = Product
        fields = ["id", "name", "price", "discounted_price", "model_number", "images"]

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False, read_only = True)
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "product"]

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    delivery_price = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ["total_price", "items_count", "order_items", "delivery_price"]
    
    def get_total_price(self, obj):
        return obj.get_cart_total_price()
    
    def get_items_count(self, obj):
        return obj.get_cart_items_count()
    
    def get_delivery_price(self, obj):
        return Order.get_delivery_price(obj.get_cart_total_price())
