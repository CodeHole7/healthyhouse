# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-03 10:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_laboratory',
            field=models.BooleanField(default=False, verbose_name='Laboratory Status'),
        ),
    ]
