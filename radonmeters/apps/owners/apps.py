from django.apps import AppConfig


class OwnerConfig(AppConfig):
    name = 'owners'

    def ready(self):
        super().ready()

        # noinspection PyUnresolvedReferences
        import owners.signals
