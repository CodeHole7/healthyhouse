from decimal import Decimal as D

from oscar.apps.basket.abstract_models import AbstractLine


class Line(AbstractLine):

    def get_price_breakdown(self):
        """
        Overridden for adding checks on negatives values for:
        - `_affected_quantity`;
        - `quantity_without_discount`;
        """

        # All next lines taken from base class,
        # except checking on min value via `max(...`.

        if not self.is_tax_known:
            raise RuntimeError("A price breakdown can only be determined "
                               "when taxes are known")
        prices = []
        if not self.discount_value:
            prices.append((
                self.unit_price_incl_tax,
                self.unit_price_excl_tax,
                max(self.quantity, 0)))
        else:
            item_incl_tax_discount = (
                self.discount_value / int(self._affected_quantity))
            item_excl_tax_discount = item_incl_tax_discount * self._tax_ratio
            item_excl_tax_discount = item_excl_tax_discount.quantize(D('0.01'))

            prices.append((
                self.unit_price_incl_tax - item_incl_tax_discount,
                self.unit_price_excl_tax - item_excl_tax_discount,
                max(self._affected_quantity, 0)))

            if self.quantity_without_discount:
                prices.append((
                    self.unit_price_incl_tax,
                    self.unit_price_excl_tax,
                    max(self.quantity_without_discount, 0)))

        return prices


# noinspection PyUnresolvedReferences
from oscar.apps.order.models import *
