from django.db.models.signals import pre_save
from django.dispatch import receiver
from oscar.apps.order.signals import order_placed
from oscar.core.loading import get_model

from config import settings


@receiver(order_placed)
def init_order_line_products(sender, **kwargs):
    """
    Generates a list of objects for each item in the order,
    right after order has been placed.

    Generated objects needed for storing info about each item in the order.
    For example `serial_number` of product.

    Added default owner

    :param sender: Instance which init call.
    :param kwargs: {
        'signal': <django.dispatch.dispatcher.Signal object at 0x1052bab38>,
        'order': <Order: #100003>,
        'user': <SimpleLazyObject: <User: admin>>
    }
    """

    # Import models.
    _DefaultProduct = get_model('catalogue', 'DefaultProduct')
    _Dosimeter = get_model('catalogue', 'Dosimeter')
    Owner = get_model('owners', 'Owner')

    # Lists for storing prepared instances.
    default_products = []
    dosimeters = []

    order = kwargs['order']
    # Preparing instances (based on class of product in the each line).
    for line in order.lines.all():
        if line.product.product_class.name == settings.OSCAR_PRODUCT_TYPE_DEFAULT:
            for i in range(line.quantity):
                default_products.append(_DefaultProduct(line_id=line.pk))
        elif line.product.product_class.name == settings.OSCAR_PRODUCT_TYPE_DOSIMETER:
            for i in range(line.quantity):
                dosimeters.append(_Dosimeter(line_id=line.pk))

    # Create all prepared instances per two requests to db.
    _DefaultProduct.objects.bulk_create(default_products)
    _Dosimeter.objects.bulk_create(dosimeters)

    # set default owner
    order.owner = Owner.default_owner()
    order.save()
