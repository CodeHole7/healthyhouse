# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-25 14:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0006_auto_20170504_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='DosimeterCondition',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('offer.condition',),
        ),
    ]
