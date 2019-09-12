from django.conf import settings
from django.utils.translation import ugettext as _
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')
Range = get_model('offer', 'Range')
CountCondition = get_model('offer', 'CountCondition')


class DosimeterCondition(CountCondition):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set minimum quantity of products for getting discount.
        self.value = settings.DOSIMETER_BENEFIT_CONDITIONS[0].low

        # Set the list of products which can have a discount.
        range_id = kwargs.get('range_id')
        if range_id:
            self.products = Range.objects.get(id=range_id).all_products()
        else:
            self.products = Product.objects.none()

    @property
    def name(self):
        return _("Condition for dosimeters")

    def is_satisfied(self, offer, basket):
        """
        Determines whether a given basket meets this condition
        """
        for line in basket.all_lines():
            if self.can_apply_condition(line):
                return True
        return False

    def can_apply_condition(self, line):
        if line.product in self.products and line.quantity >= self.value:
            return True
        else:
            return False
