# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-01 18:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShortenedURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_url', models.URLField(unique=True)),
                ('short_id', models.CharField(max_length=10, unique=True)),
            ],
        ),
    ]