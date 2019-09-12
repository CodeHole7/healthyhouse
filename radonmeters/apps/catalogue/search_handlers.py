from oscar.core.loading import get_class
from oscar.core.loading import get_model

from catalogue.forms import SortForm

Product = get_model('catalogue', 'Product')
BaseSimpleProductSearchHandler = get_class(
    'catalogue.search_handlers', 'SimpleProductSearchHandler')


class SimpleProductSearchHandler(BaseSimpleProductSearchHandler):

    def __init__(self, request_data, full_path, categories=None):
        self.sort_by = request_data.get('sort_by')
        super().__init__(request_data, full_path, categories)

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date_updated')

        if self.sort_by in SortForm.CHOICES._db_values:
            qs = qs.order_by(self.sort_by)

        return qs
