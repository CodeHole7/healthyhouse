from django.apps import AppConfig


class InstructionsConfig(AppConfig):
    name = 'instructions'

    def ready(self):
        super().ready()

        from instructions import signals
