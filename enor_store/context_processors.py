from .models import Product
from category.models import Category
import json

def products_processor(request):
    return {
        'static_products': Product.objects.all(),
        'static_products_json':json.dumps(list(Product.objects.values()), sort_keys=True, default=str)
    }


def categories_processor(request):
    return {
        'static_categories': Category.objects.all(),
        'static_categories_json':json.dumps(list(Category.objects.values()), sort_keys=True, default=str)
    }
