from django.conf import settings
from django.contrib import messages
from django.urls.base import reverse_lazy
from django.utils.translation import ugettext as _
from django.views import generic
from oscar.views import sort_queryset

from catalogue.models import DefaultProduct
from dashboard.default_products.forms import DefaultProductChangeForm
from dashboard.default_products.forms import DefaultProductSearchForm


class DefaultProductListView(generic.ListView):
    """
    View for representation default_products in the Oscar's Dashboard.
    """

    # It's taken from default realisation for
    # the same functionality (partners app).

    model = DefaultProduct
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
    form_class = DefaultProductSearchForm
    context_object_name = 'default_products'
    template_name = 'dashboard/default_products/default_product_list.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form = None
        self.description = None
        self.is_filtered = None

    def get_queryset(self):
        qs = self.model._default_manager.all()
        qs = sort_queryset(qs, self.request, ['-created'])

        self.description = _("All default products")

        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['id']:
            qs = qs.filter(id=data['id'])
            self.description = _("Default products matching '%s'") % data['id']
            self.is_filtered = True

        if data['serial_number']:
            qs = qs.filter(serial_number=data['serial_number'])
            self.description = _("Default products matching '%s'") % data['serial_number']
            self.is_filtered = True

        if data['order_number']:
            qs = qs.filter(line__order__number=data['order_number'])
            self.description = _("Default products matching '%s'") % data['order_number']
            self.is_filtered = True

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['is_filtered'] = self.is_filtered
        context['queryset_description'] = self.description
        return context


class DefaultProductUpdateView(generic.UpdateView):
    """
    View for updating default_products in the Oscar's Dashboard.
    """

    model = DefaultProduct
    form_class = DefaultProductChangeForm
    success_url = reverse_lazy('dashboard:default-product-list')
    context_object_name = 'default_product'
    template_name = 'dashboard/default_products/default_product_detail.html'

    def form_valid(self, form):
        # Replace `success_url` if form has `next_url`.
        next_url = self.request.POST.get('next_url')
        if next_url is not None:
            self.success_url = next_url

        # Create success message for admin.
        messages.success(
            request=self.request,
            message=_('Default product "%s" has been successfully updated.') % self.object.id)

        # Return to default behavior for `form_valid`.
        return super().form_valid(form)
