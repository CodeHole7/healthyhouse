# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-23 06:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0027_auto_20171020_1456'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='description_nb',
        ),
        migrations.RemoveField(
            model_name='category',
            name='name_nb',
        ),
        migrations.RemoveField(
            model_name='product',
            name='description_nb',
        ),
        migrations.RemoveField(
            model_name='product',
            name='lead_nb',
        ),
        migrations.RemoveField(
            model_name='product',
            name='product_usage_nb',
        ),
        migrations.RemoveField(
            model_name='product',
            name='specification_nb',
        ),
        migrations.RemoveField(
            model_name='product',
            name='title_nb',
        ),
    ]
