# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-31 12:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0042_remove_dosimeter_report_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dosimeter',
            name='yearly_avg',
        ),
    ]
