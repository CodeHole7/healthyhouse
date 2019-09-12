# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations

from oscar.core.loading import get_model

# Import classes
Range = get_model('offer', 'Range')
ProductClass = get_model('catalogue', 'ProductClass')
ProductAttribute = get_model('catalogue', 'ProductAttribute')


def _update_product_class(product_class):
    for range_obj in Range.objects.filter(slug='dosimeters'):
        for product in range_obj.included_products.all():
            # Save current promo image
            _promo_image = getattr(product.attr, 'promo_image', None)

            # Change product type.
            product.product_class = product_class
            product.save()

            # Set old promo image if it exists.
            if _promo_image:
                product.attr.promo_image = _promo_image
                product.save()


def upgrade_product_class(apps, schema_editor):
    # Get or create ProductClass for "Dosimeter" products.
    pc, created = ProductClass.objects.get_or_create(
        name=settings.OSCAR_PRODUCT_TYPE_DOSIMETER)

    if created:
        ProductAttribute.objects.create(
            product_class=pc,
            name='Promotion Image',
            code='promo_image',
            type='image')

    # Update objects.
    _update_product_class(pc)


def downgrade_product_class(apps, schema_editor):
    # Get or create ProductClass for "Default" products.
    pc, created = ProductClass.objects.get_or_create(
        name=settings.OSCAR_PRODUCT_TYPE_DEFAULT)

    if created:
        ProductAttribute.objects.create(
            product_class=pc,
            name='Promotion Image',
            code='promo_image',
            type='image')

    # Update objects.
    _update_product_class(pc)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0034_auto_20171026_0919'),
        ('offer', '0015_delete_vouchercustombenefit'),
    ]

    operations = [
        migrations.RunPython(upgrade_product_class, downgrade_product_class)
    ]
