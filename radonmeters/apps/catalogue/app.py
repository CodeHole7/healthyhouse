from oscar.apps.catalogue.app import CatalogueApplication as DefaultCatalogueApplication


class CatalogueApplication(DefaultCatalogueApplication):
    """
    Overwritten for adding translation fields of RawHTML (in translation.py).
    """
    pass


application = CatalogueApplication()
