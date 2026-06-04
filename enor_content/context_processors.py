from .models import Social_links

def social_links_processor(request):
    return {
        'social_links': Social_links.objects.filter(is_active=True),
    }