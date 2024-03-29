# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-03 12:02
from __future__ import unicode_literals

import common.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Phone number in the international format.', max_length=15, validators=[common.validators.PhoneNumberValidator()], verbose_name='Phone Number'),
        ),
    ]
