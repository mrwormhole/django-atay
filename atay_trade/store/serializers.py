from .models import Order, OrderItem, Product
from rest_framework import serializers

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = []

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = []

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = []