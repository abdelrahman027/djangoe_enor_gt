from django.apps import AppConfig


class EnorProfileConfig(AppConfig):
    name = 'enor_profile'

    def ready(self):
        import enor_profile.signals