# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-26 11:06
from __future__ import unicode_literals

import common.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0004_auto_20170226_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Phone number in the international format.', max_length=15, validators=[common.validators.PhoneNumberValidator()], verbose_name='Phone Number'),
        ),
    ]
