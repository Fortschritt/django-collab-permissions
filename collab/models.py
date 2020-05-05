# -*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Collab(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_manager = models.BooleanField(verbose_name="is Manager", default=False)
    last_activity = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    def update_last_activity(self):
        update_interval = getattr(settings, "COLLAB_LAST_ACTIVITY_UPDATE_INTERVAL", 600) # seconds
        now = timezone.now()
        if (self.last_activity - timedelta(seconds=update_interval)) < now:
            self.last_activity = now
            self.save()
