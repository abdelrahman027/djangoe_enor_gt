from django.core.mail import EmailMultiAlternatives




def send_html_email(subject, message, from_email, to_email, html_message):
    msg = EmailMultiAlternatives(subject, message, from_email, [to_email])
    msg.attach_alternative(html_message, "text/html")
    msg.send()