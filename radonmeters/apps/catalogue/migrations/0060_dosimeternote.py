# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-10-16 14:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0059_auto_20191003_1216'),
    ]

    operations = [
        migrations.CreateModel(
            name='DosimeterNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_type', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('dosimeter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.Dosimeter')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]