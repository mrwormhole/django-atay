from django.urls import path
from . import views

urlpatterns = [
    path("", views.store, name="store"),
    path("checkout/", views.checkout, name="checkout"),
    path("contact/", views.contact, name="contact"),
    path("catalog/", views.catalog, name="catalog"),
    path("product/", views.product, name="product")
]