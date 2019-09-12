# -*- coding: utf-8 -*-
from django.db import migrations
from django.db.models import Q


def set_data(apps, schema_editor):
    Line = apps.get_model('order', 'Line')

    # Add title and upc for all records without it,
    # we cannot use `F(product__upc)` with `Line.objects.update()`.
    for l in Line.objects.filter(Q(title='') | Q(upc='')):
        l.title = l.product.title
        l.upc = l.product.upc
        l.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0018_remove_line_report_pdf'),
    ]

    operations = [
        migrations.RunPython(set_data, do_nothing)
    ]
