# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-10-02 00:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0054_auto_20190831_0639'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batch',
            name='batch_name',
        ),
        migrations.AddField(
            model_name='batch',
            name='batch_description',
            field=models.CharField(default=False, max_length=512, verbose_name='Batch Description'),
        ),
    ]