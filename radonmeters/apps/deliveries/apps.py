from django.apps import AppConfig


class DeliveriesConfig(AppConfig):
    name = 'deliveries'

    def ready(self):
        super().ready()
        from deliveries import tasks
