# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-14 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0024_order_approved_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='not_weird',
            field=models.BooleanField(default=False, verbose_name='Not weird?'),
        ),
        migrations.AddField(
            model_name='order',
            name='not_weird_explanation',
            field=models.CharField(blank=True, max_length=255, verbose_name='Why not weird'),
        ),
    ]
