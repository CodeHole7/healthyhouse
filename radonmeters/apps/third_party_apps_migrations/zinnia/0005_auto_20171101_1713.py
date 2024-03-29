# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-01 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zinnia', '0004_on_delete_arg'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description_da',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='category',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='category',
            name='description_nn',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='category',
            name='description_sv',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='category',
            name='title_da',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='category',
            name='title_en',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='category',
            name='title_nn',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='category',
            name='title_sv',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='entry',
            name='content_da',
            field=models.TextField(blank=True, null=True, verbose_name='content'),
        ),
        migrations.AddField(
            model_name='entry',
            name='content_en',
            field=models.TextField(blank=True, null=True, verbose_name='content'),
        ),
        migrations.AddField(
            model_name='entry',
            name='content_nn',
            field=models.TextField(blank=True, null=True, verbose_name='content'),
        ),
        migrations.AddField(
            model_name='entry',
            name='content_sv',
            field=models.TextField(blank=True, null=True, verbose_name='content'),
        ),
        migrations.AddField(
            model_name='entry',
            name='lead_da',
            field=models.TextField(blank=True, help_text='Lead paragraph', null=True, verbose_name='lead'),
        ),
        migrations.AddField(
            model_name='entry',
            name='lead_en',
            field=models.TextField(blank=True, help_text='Lead paragraph', null=True, verbose_name='lead'),
        ),
        migrations.AddField(
            model_name='entry',
            name='lead_nn',
            field=models.TextField(blank=True, help_text='Lead paragraph', null=True, verbose_name='lead'),
        ),
        migrations.AddField(
            model_name='entry',
            name='lead_sv',
            field=models.TextField(blank=True, help_text='Lead paragraph', null=True, verbose_name='lead'),
        ),
        migrations.AddField(
            model_name='entry',
            name='title_da',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='entry',
            name='title_en',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='entry',
            name='title_nn',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='entry',
            name='title_sv',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
    ]
