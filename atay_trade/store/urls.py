from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "store"

urlpatterns = [
    path("", views.store, name="store"),
    path("cart/", views.CartList.as_view()),
    path("cart/add/", views.CartAdd.as_view()),
    path("cart/remove/", views.CartRemove.as_view()),
    path("checkout/", views.checkout, name="checkout"),
    path("contact/", views.contact, name="contact"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<str:category>", views.catalog, name="catalogByCategory"),
    path("products/<int:id>", views.product, name="product"),
    path("signup/", views.signup, name="signup"),
    path("account/", views.account, name="account"),
    path("login/", auth_views.LoginView.as_view(template_name="store/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="store/index.html"), name="logout"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add/", views.wishlistAdd),
    path("wishlist/remove/", views.wishlistRemove),
    path("orders/process/", views.processOrder),
    path("stocks/check/", views.checkStocks),
    path("invoices/<str:transaction_id>", views.invoice, name="invoice")
]