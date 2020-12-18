from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.store, name="store"),
    path("cart/", views.cart), # this is more like API than view
    path("checkout/", views.checkout, name="checkout"),
    path("contact/", views.contact, name="contact"),
    path("catalog/", views.catalog, name="catalog"),
    path("product/", views.product, name="product")
]