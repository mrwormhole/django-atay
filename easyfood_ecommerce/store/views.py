from django.shortcuts import render

def store(request):
    context = {}
    render(request, "store/store.html", context)

def checkout(request):
    context = {}
    render(request, "store/checkout.html", context)

def cart(request):
    context = {}
    render(request, "store/cart.html", context)

