from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.http import JsonResponse
from django.urls.base import reverse
from django.urls.base import reverse_lazy
from django.utils.translation import ugettext as _
from django.views import generic
from oscar.core.loading import get_model
from oscar.views import sort_queryset

from dashboard.deliveries.forms import ShipmentChangeForm
from dashboard.deliveries.forms import ShipmentReturnChangeForm
from dashboard.deliveries.forms import ShipmentCreateForm
from dashboard.deliveries.forms import ShipmentSearchForm
from dashboard.deliveries.forms import ShipmentReturnCreateForm

Shipment = get_model('deliveries', 'Shipment')
ShipmentReturn = get_model('deliveries', 'ShipmentReturn')


class ShipmentListView(generic.ListView):
    """
    View for representation deliveries in the Oscar's Dashboard.
    """

    # It's taken from default realisation for
    # the same functionality (partners app).

    model = Shipment
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
    form_class = ShipmentSearchForm
    context_object_name = 'shipments'
    template_name = 'dashboard/deliveries/shipment_list.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form = None
        self.description = None
        self.is_filtered = None

    def get_queryset(self):
        qs = self.model._default_manager.all()
        qs = sort_queryset(qs, self.request, ['-created'])

        self.description = _("All shipments")

        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['id']:
            qs = qs.filter(id=data['id'])
            self.description = _("Shipments matching '%s'") % data['id']
            self.is_filtered = True

        if data['order_number']:
            qs = qs.filter(order__number=data['order_number'])
            self.description = _("Shipments matching '%s'") % data['order_number']
            self.is_filtered = True

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['is_filtered'] = self.is_filtered
        context['queryset_description'] = self.description
        return context


class ShipmentCreateView(generic.CreateView):
    """
    View for creating deliveries in the Oscar's Dashboard.
    """

    template_name = 'dashboard/deliveries/shipment_change_form.html'
    form_class = ShipmentCreateForm

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            return super().post(request, *args, **kwargs)
        else:
            raise Http404

    def form_valid(self, form):
        self.object = form.save()
        data = {
            'message': _('Shipment has been successfully added.'),
            'url': reverse(
                'dashboard:shipment-update',
                kwargs={'pk': self.object.pk})}
        return JsonResponse(data=data, status=201)

    def form_invalid(self, form):
        data = {'errors': form.errors}
        return JsonResponse(data=data, status=400)


class ShipmentUpdateView(generic.UpdateView):
    """
    View for updating deliveries in the Oscar's Dashboard.
    """

    model = Shipment
    form_class = ShipmentChangeForm
    success_url = reverse_lazy('dashboard:shipment-list')
    context_object_name = 'shipment'
    template_name = 'dashboard/deliveries/shipment_change_form.html'

    def form_valid(self, form):

        # Create success message for admin.
        messages.success(
            request=self.request,
            message=_('Shipment "%s" has been successfully updated.') % self.object.id)

        # Return to default behavior for `form_valid`.
        return super().form_valid(form)


class ShipmentDeleteView(generic.DeleteView):
    """
    View for deleting deliveries in the Oscar's Dashboard.
    """

    model = Shipment
    success_url = reverse_lazy('dashboard:shipment-list')
    template_name = 'dashboard/deliveries/shipment_change_form.html'


class ShipmentReturnCreateView(generic.CreateView):
    """
    View for creating deliveries in the Oscar's Dashboard.
    """
    form_class = ShipmentReturnCreateForm

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            return super().post(request, *args, **kwargs)
        else:
            raise Http404

    def form_valid(self, form):
        self.object = form.save()
        data = {
            'message': _('Return shipment has been successfully added.'),
        }
        return JsonResponse(data=data, status=201)

    def form_invalid(self, form):
        data = {'errors': form.errors}
        return JsonResponse(data=data, status=400)


class ShipmentReturnUpdateView(generic.UpdateView):
    model = ShipmentReturn
    form_class = ShipmentReturnChangeForm
    success_url = reverse_lazy('dashboard:order-list')
    context_object_name = 'shipment'
    template_name = 'dashboard/deliveries/shipment_return_change_form.html'

    def form_valid(self, form):
        # Create success message for admin.
        messages.success(
            request=self.request,
            message=_('Shipment "%s" has been successfully updated.') % self.object.id)

        # Return to default behavior for `form_valid`.
        return super().form_valid(form)

class ShipmentReturnDeleteView(generic.DeleteView):
    """
    View for deleting deliveries in the Oscar's Dashboard.
    """

    model = ShipmentReturn
    success_url = reverse_lazy('dashboard:order-list')
    template_name = 'dashboard/deliveries/shipment_return_change_form.html'