# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-09-28 03:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('owners', '0004_auto_20180619_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Staff'),
        ),
    ]
