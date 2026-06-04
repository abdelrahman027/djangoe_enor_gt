
from django.contrib.auth.models import User
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from .models import UserProfile
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from django.conf import settings

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    user=instance
    if created:
        UserProfile.objects.create(user=user,email=user.email)
    else:
        profile=get_object_or_404(UserProfile,user=user)
        profile.email=user.email
        profile.save()
        
@receiver(post_save, sender=UserProfile)
def update_user(sender, instance, created, **kwargs):
    profile=instance
    if created == False:
        user = profile.user
        if user.email!=profile.email:
            user.email=profile.email
            user.save()


@receiver(post_delete, sender=User)
def delete_profile_on_user_delete(sender, instance, **kwargs):
    try:
        # Assuming Employee has a OneToOneField to User
        profile = UserProfile.objects.get(user=instance)
        profile.delete()  # This will delete the Employee instance
    except UserProfile.DoesNotExist:
        pass  # If no Employee exists for the user, just do nothing
    