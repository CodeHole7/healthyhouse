from decimal import Decimal

from django.conf import settings
from oscar.apps.partner import strategy


class Selector:
    """
    Custom selector to return a DA-specific strategy that charges VAT.
    """

    def strategy(self, request=None, user=None, **kwargs):
        return DAStrategy()


class IncludingDAVAT(strategy.FixedRateTax):
    """
    Price policy to charge VAT on the base price.
    """
    # We can simply override the tax rate on the core FixedRateTax.  Note
    # this is a simplification: in reality, you might want to store tax
    # rates and the date ranges they apply in a database table.  Your
    # pricing policy could simply look up the appropriate rate.
    rate = Decimal(settings.VAT_PERCENT_DA)


class DAStrategy(
        strategy.UseFirstStockRecord,
        IncludingDAVAT,
        strategy.StockRequired,
        strategy.Structured):
    """
    Typical DA strategy for physical goods.

    - There's only one warehouse/partner so we use the first and only stock record.
    - Enforce stock level. Don't allow purchases when we don't have stock.
    - Charge DA VAT on prices. Assume everything is standard-rated.
    """
