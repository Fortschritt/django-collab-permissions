# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-19 10:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0002_auto_20151102_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='collab',
            name='last_activity',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
