from oscar.apps.order.utils import OrderCreator as BaseOrderCreator


class OrderCreator(BaseOrderCreator):
    """
    Overridden for adding hack into `create_line_price_models` method.
    Needed for excluding negative value in `quantity` field.
    """

    def create_line_price_models(self, order, order_line, basket_line):
        breakdown = basket_line.get_price_breakdown()
        for price_incl_tax, price_excl_tax, quantity in breakdown:
            order_line.prices.create(
                order=order,
                quantity=max(quantity, 0),
                price_incl_tax=price_incl_tax,
                price_excl_tax=price_excl_tax)
