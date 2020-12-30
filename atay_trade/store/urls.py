from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.store, name="store"),
    path("cart/", views.CartList.as_view()),
    path("checkout/", views.checkout, name="checkout"),
    path("contact/", views.contact, name="contact"),
    path("catalog/", views.catalog, name="catalog"),
    path("products/<int:id>", views.product, name="product")
]