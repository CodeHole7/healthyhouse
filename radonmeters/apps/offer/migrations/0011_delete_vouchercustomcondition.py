# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-12 11:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0010_create_range_with_all_products_py'),
    ]

    operations = [
        migrations.DeleteModel(
            name='VoucherCustomCondition',
        ),
    ]
