# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-02-23 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0030_auto_20190129_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='external_report_pdf',
            field=models.FileField(blank=True, upload_to='reports/external/', verbose_name='External report'),
        ),
        migrations.AddField(
            model_name='order',
            name='use_external_report',
            field=models.BooleanField(default=False, verbose_name='Use external report?'),
        ),
    ]