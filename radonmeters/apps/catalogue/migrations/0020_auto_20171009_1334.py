# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-09 13:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0018_dosimeter_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dosimeter',
            options={'ordering': ('-line__order__date_placed', '-created')},
        ),
    ]