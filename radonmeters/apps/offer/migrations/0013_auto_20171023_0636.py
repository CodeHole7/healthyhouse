# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-23 06:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0012_auto_20171020_1456'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conditionaloffer',
            name='description_nb',
        ),
        migrations.RemoveField(
            model_name='conditionaloffer',
            name='name_nb',
        ),
        migrations.RemoveField(
            model_name='range',
            name='description_nb',
        ),
        migrations.RemoveField(
            model_name='range',
            name='name_nb',
        ),
    ]