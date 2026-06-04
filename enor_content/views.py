from enor_content.models import Social_links
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FAQ,Newsletter
from .forms import ContactForm,NesletterForm
from enor_core.utils import send_html_email
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags        
def contact_us(request):
    faqs = FAQ.objects.filter(is_active=True)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact=form.save()
            # === Send Email ===
            subject = f"📩 New Contact: {contact.subject}"
            html_content = render_to_string('emails/contact_notification_email.html', {
                'contact': contact,
            })
            text_content = strip_tags(html_content)
            send_html_email(subject, text_content, settings.DEFAULT_FROM_EMAIL, "abdelrahmansaad027@gmail.com", html_content)
            
            messages.success(request, 'Thank you! We’ll get back to you soon.')
            return redirect('contact_us')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {
        'faqs': faqs,
        'form': form,

    })
    
    
def newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        Newsletter.objects.create(email=email)
        if email:
            messages.success(request, 'You are now subscribed to our newsletter.')
    return redirect('home')
