# -*- coding: utf-8 -*-

from django.db import IntegrityError
from django.db import migrations
from oscar.core.loading import get_model

# Import classes
Range = get_model('offer', 'Range')


def create_range(apps, schema_editor):
    try:
        Range.objects.create(
            name='ALL PRODUCTS',
            description='ALL PRODUCTS',
            includes_all_products=True)
    except IntegrityError:
        pass


def remove_range(apps, schema_editor):
    Range.objects.filter(
        name='ALL PRODUCTS',
        description='ALL PRODUCTS',
        includes_all_products=True).delete()


class Migration(migrations.Migration):
    dependencies = [('offer', '0015_delete_vouchercustombenefit')]

    operations = [migrations.RunPython(create_range, remove_range)]
