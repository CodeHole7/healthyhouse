import operator

from django.utils.translation import ugettext as _
from oscar.apps.offer import benefits
from oscar.apps.offer import results
from oscar.apps.offer import utils
from oscar.core.loading import get_model

from config import settings

PercentageDiscountBenefit = get_model('offer', 'PercentageDiscountBenefit')


class DosimeterBenefit(PercentageDiscountBenefit):
    """
    Provides logic of discount system based on quantity of ordered product.
    """

    class Meta:
        proxy = True

    @staticmethod
    def _get_discount_percent(quantity: int=0):
        for c in settings.DOSIMETER_BENEFIT_CONDITIONS:
            if c.low <= quantity < c.high:
                return min(benefits.D(c.percent), benefits.D('100.0'))
        else:
            return benefits.D('0.0')

    @property
    def name(self):
        return _('Different discount based on quantity of ordered dosimeters.')

    @property
    def description(self):
        return _('Provides different discount based on number of dosimeters.')

    def get_applicable_lines(self, offer, basket, range=None):
        """
        Return the basket lines that are available to be discounted

        :basket: The basket
        :range: The range of products to use for filtering.  The fixed-price
                benefit ignores its range and uses the condition range
        """
        if range is None:
            range = self.range

        line_tuples = []

        for line in basket.all_lines():
            product = line.product

            if product.product_class.slug != settings.OSCAR_PRODUCT_TYPE_DOSIMETER.lower():
                continue

            if not range.contains(product):
                continue

            price = utils.unit_price(offer, line)
            if not price:
                # Avoid zero price products
                continue

            line_tuples.append((price, line))

        # We sort lines to be cheapest first to ensure consistent applications
        return sorted(line_tuples, key=operator.itemgetter(0))

    def apply(
            self,
            basket,
            condition,
            offer,
            discount_percent=None,
            max_total_discount=None):
        """
        Overrides default logic for implement opportunity to use
        custom discount system.
        """

        discount_amount_available = max_total_discount
        line_tuples = self.get_applicable_lines(offer, basket)
        discount = benefits.D('0.00')
        max_affected_items = self._effective_max_affected_items()
        affected_items = 0
        affected_lines = []

        for price, line in line_tuples:

            # Calculate discount percent by quantity.
            discount_percent = self._get_discount_percent(quantity=line.quantity)

            # Validate that discount is available
            if affected_items >= max_affected_items:
                break
            if discount_amount_available == 0:
                break

            quantity_affected = min(
                line.quantity,
                max_affected_items - affected_items)

            line_discount = self.round(
                discount_percent / benefits.D('100.0')
                * price
                * int(quantity_affected))

            if discount_amount_available is not None:
                line_discount = min(line_discount, discount_amount_available)
                discount_amount_available -= line_discount

            benefits.apply_discount(line, line_discount, quantity_affected)

            affected_lines.append((line, line_discount, quantity_affected))
            affected_items += quantity_affected
            discount += line_discount

        if discount > 0:
            condition.consume_items(offer, basket, affected_lines)

        return results.BasketDiscount(discount)
