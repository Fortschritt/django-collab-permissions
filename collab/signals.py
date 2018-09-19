from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from actstream.signals import action
from spaces.models import Space
from .models import Collab

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auth_post_save_reveiver(sender, instance, created, **kwargs):
    if created:
        myargs = {}
        if "is_manager" in kwargs.keys():
            myargs["is_manager"] = kwargs["is_manager"]
        Collab.objects.create(user=instance, **myargs)

@receiver(post_save, sender=Space)
def space_post_save_receiver(sender, instance, created, **kwargs):
    verb = "was created" if created == True else "was updated"
    action.send(instance, verb=verb)