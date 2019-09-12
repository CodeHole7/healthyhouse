from django.contrib.flatpages.models import FlatPage
from oscar.apps.offer.models import Range


def additional_data(request):
    # Add Flatpages (grouped by root url).
    data = {
        'fp_legal': FlatPage.objects.filter(url__istartswith='/legal/'),
        'fp_b2b': FlatPage.objects.filter(url__istartswith='/b2b/'),
    }

    # Add footer_products.
    range_obj = Range.objects.filter(slug='products_for_footer').first()
    if range_obj:
        data['footer_products'] = range_obj.included_products.all()

    return data
