# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-08-31 02:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0052_batch_batch_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='batch',
            old_name='batch_owner_id',
            new_name='batch_owner',
        ),
        migrations.RenameField(
            model_name='batch_dosimeter',
            old_name='batch_id',
            new_name='batch',
        ),
        migrations.RenameField(
            model_name='batch_dosimeter',
            old_name='dosimeter_id',
            new_name='dosimeter',
        ),
    ]
