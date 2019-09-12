# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-05 14:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0008_dosimeterbenefit'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoucherCustomBenefit',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('offer.percentagediscountbenefit',),
        ),
        migrations.CreateModel(
            name='VoucherCustomCondition',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('offer.countcondition',),
        ),
    ]