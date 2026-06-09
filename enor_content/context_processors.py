from .models import Social_links

def social_links_processor(request):
    return {
        'social_links': Social_links.objects.filter(is_active=True),
    }
    

def contact_info_processor(request):
    return {
        'contact_info': {
            'email': 'Enorfitness1@gmail.com',
            'whatsapp': '01212443372',
            'instagram': 'https://www.instagram.com/enor_fitness?igsh=MWw5ZnQwdTkxenNndQ==',
        }
    }