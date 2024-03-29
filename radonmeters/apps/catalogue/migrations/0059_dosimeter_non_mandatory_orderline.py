# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-10-13 19:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0058_auto_20191002_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='created_date',
            field=models.DateField(default=datetime.datetime(2019, 10, 13, 19, 37, 26, 426117, tzinfo=utc), null=True, verbose_name='Date of creation'),
        ),
        migrations.AlterField(
            model_name='dosimeter',
            name='line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dosimeters', to='order.Line', verbose_name='Line'),
        ),
    ]
