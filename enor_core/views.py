from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    products = [
        {
            "name": "Performance Hoodie",
            "category": "Apparel",
            "price": "AED 199",
            "original_price": "AED 249",
            "rating": 4,
            "on_sale": True,
            "initial": "H"
        },
        {
            "name": "Boost Wireless Earbuds",
            "category": "Electronics",
            "price": "AED 299",
            "rating": 5,
            "on_sale": False,
            "initial": "E"
        },
        {
            "name": "Tech Backpack Pro",
            "category": "Gear",
            "price": "AED 349",
            "original_price": "AED 399",
            "rating": 4,
            "on_sale": True,
            "initial": "B"
        },
        {
            "name": "Hydration Smart Bottle",
            "category": "Lifestyle",
            "price": "AED 129",
            "rating": 4,
            "on_sale": False,
            "initial": "W"
        }
    ]
    return render(request,"index.html",{"products":products})