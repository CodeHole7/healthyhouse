from oscar.apps.catalogue.config import CatalogueConfig as CoreCatalogueConfig


class CatalogueConfig(CoreCatalogueConfig):
    name = 'catalogue'

    def ready(self):
        super().ready()

        # noinspection PyUnresolvedReferences
        import catalogue.signals
        import catalogue.tasks
