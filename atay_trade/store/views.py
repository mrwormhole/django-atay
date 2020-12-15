from django.shortcuts import render

def store(request):
    context = {}
    return render(request, "store/index.html", context)

def checkout(request):
    context = {}
    return render(request, "store/checkout.html", context)

def contact(request):
    context = {}
    return render(request, "store/contact.html", context)

def catalog(request):
    context = {}
    return render(request, "store/catalog.html", context)

def product(request):
    context = {}
    return render(request, "store/product.html", context)
