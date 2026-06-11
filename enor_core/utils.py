from django.core.mail import EmailMultiAlternatives




def send_html_email(subject, message, from_email, to_email, html_message):
    msg = EmailMultiAlternatives(subject, message, from_email, [to_email])
    msg.attach_alternative(html_message, "text/html")
    msg.send()
    
    
import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]


def send_resend_email(subject, from_email, to_email, html_message):
    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_message,
    }
    email = resend.Emails.send(params)
    print(email)