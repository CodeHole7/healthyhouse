from django.views.generic.edit import FormMixin
from oscar.core.loading import get_class

SortForm = get_class('catalogue.forms', 'SortForm')
BaseCatalogueView = get_class('catalogue.views', 'CatalogueView')
BaseProductCategoryView = get_class('catalogue.views', 'ProductCategoryView')


class CatalogueView(FormMixin, BaseCatalogueView):
    form_class = SortForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(initial=self.request.GET)
        return context


class ProductCategoryView(FormMixin, BaseProductCategoryView):
    form_class = SortForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(initial=self.request.GET)
        return context
