from oscar.apps.order.config import OrderConfig as CoreOrderConfig


class OrderConfig(CoreOrderConfig):
    name = 'order'

    def ready(self):
        super().ready()

        # noinspection PyUnresolvedReferences
        import order.signals
