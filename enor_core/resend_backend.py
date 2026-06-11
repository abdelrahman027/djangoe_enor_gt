from django.core.mail.backends.base import BaseEmailBackend
import requests
import os

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

class ResendBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0

        for message in email_messages:
            try:
                response = requests.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": message.from_email,
                        "to": message.to,
                        "subject": message.subject,
                        "html": message.body,
                    },
                )

                if response.status_code == 200:
                    sent_count += 1

            except Exception:
                if not self.fail_silently:
                    raise

        return sent_count