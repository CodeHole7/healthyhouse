# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-23 11:10
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0031_auto_20171023_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='category',
            name='description_da',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='category',
            name='description_en',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='category',
            name='description_nn',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='category',
            name='description_sv',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Description'),
        ),
    ]
