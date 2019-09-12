from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls.base import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView, ModelFormMixin

from oscar.core.loading import get_model

from dashboard.owners.forms import OwnerDashboardSearchForm, \
    OwnerDashboardEmailConfigForm
from owners.forms import OwnerDetailForm
from owners.forms import OwnerPDFReportThemeForm
from owners.models import Owner, OwnerEmailConfig
from owners.models import OwnerPDFReportTheme
from order.models import filter_ready_for_approval_but_not_approved, \
    filter_approved, \
    filter_slip_no_result, \
    filter_result_no_slip, \
    filter_empty, \
    filter_sent_or_reported, \
    filter_partial

Order = get_model('order', 'Order')

class OwnerDashboardListView(generic.ListView):
    """
    View for representation owners in the Oscar's Dashboard.
    """

    # It's taken from default realisation for
    # the same functionality (dosimeters app).

    model = Owner
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
    form_class = OwnerDashboardSearchForm
    context_object_name = 'owners'
    template_name = 'dashboard/owners/owner_list.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form = None
        self.description = None
        self.is_filtered = None

    """
        @author : Alex (Edited)
        @date : 2019.9.4
        @description : Edited for Owners dashboard. Admin can see all owners 
                        but staff can only see associated owners with himself.
    """
    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_superuser:
            self.description = _("All owners")
        else:
            self.description = _("My Owners")
            qs = qs.filter(user_id = self.request.user.id)

        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['id']:
            qs = qs.filter(id=data['id'])
            self.description = _("Dosimeters matching '%s'") % data['id']
            self.is_filtered = True

        if data['email']:
            qs = qs.filter(email=data['email'])
            self.description = _("Dosimeters matching '%s'") % data['email']
            self.is_filtered = True

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['is_filtered'] = self.is_filtered
        context['queryset_description'] = self.description
        return context


"""
    @author : Alex
    @date : 2019.9.4
    @description : dashboard/owners/add, update page view
                   edited because don't need to display staff list
"""
class OwnerDashboardFormView(ModelFormMixin, ProcessFormView):
    model = Owner
    fields = ['first_name', 'last_name', 'email', 'is_default']
    context_object_name = 'owner'
    template_name = 'dashboard/owners/owner_detail.html'
    success_url = reverse_lazy('dashboard:owner-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_email_config'] = OwnerDashboardEmailConfigForm
        return context



class OwnerDashboardUpdateView(OwnerDashboardFormView, generic.UpdateView):
    def form_valid(self, form):
        owner = form.save()
        owner.user_id = self.request.user.id
        owner.save()
        return HttpResponseRedirect(self.success_url)
    # pass


class OwnerDashboardCreateView(OwnerDashboardFormView, generic.CreateView):
    def form_valid(self, form):
        owner = form.save()
        owner.user_id = self.request.user.id
        owner.save()
        return HttpResponseRedirect(self.success_url)
    #pass

class OwnerDashboardEmailConfigDetailView(generic.UpdateView):
    model = OwnerEmailConfig
    template_name = 'dashboard/owners/owner_email_config.html'
    owner = None
    form_class = OwnerDashboardEmailConfigForm

    def get_object(self, queryset=None):
        self.owner = get_object_or_404(Owner, pk=self.kwargs['pk'])
        if hasattr(self.owner, 'email_config'):
            return self.owner.email_config

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['owner'] = self.owner
        return kwargs

    def get_success_url(self):
        return reverse('dashboard:owner-detail', args=(self.owner.id, ))


class OwnerPDFReportThemeListView(generic.ListView):
    model = OwnerPDFReportTheme
    template_name = 'dashboard/owners/report_template_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        return super().get_queryset().select_related('owner')


class OwnerPDFReportBaseView:
    model = OwnerPDFReportTheme
    form_class = OwnerPDFReportThemeForm
    template_name = 'dashboard/owners/report_template_detail.html'
    success_url = reverse_lazy('dashboard:owner-report-template-list')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        if 'render_preview' in self.request.POST:
            data = {'errors': form.errors}
            return JsonResponse(data=data, status=400)
        messages.error(
            self.request,
            _("The submitted form was not valid, please correct "
              "the errors and resubmit"))
        return super(OwnerPDFReportBaseView, self).form_invalid(form)

    def form_valid(self, form):
        if 'render_preview' in self.request.POST:
            return self.render_preview(form)
        return super(OwnerPDFReportBaseView, self).form_valid(form)

    def render_preview(self, form):
        form.save(commit=False)
        template = form.cleaned_data['pdf_template']
        logo = form.cleaned_data['logo']
        return form.preview_order.prepare_pdf_report_response(logo, template)


class OwnerPDFReportThemeUpdateView(OwnerPDFReportBaseView, generic.UpdateView):
    pass


class OwnerPDFReportThemeCreateView(OwnerPDFReportBaseView, generic.CreateView):
    pass

class OwnerDashboardSummaryView(TemplateView):
    template_name = 'dashboard/owners/owner_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owners_summary'] = []
        for owner in Owner.objects.all():
            queryset = Order.objects.filter(owner=owner)
            # Total
            total_orders = queryset.count()
            # Canceled orders.
            canceled_orders = queryset.filter(status='canceled')
            queryset = queryset.filter(~Q(status='canceled'))
            # Ready for approval but not approved
            ready_not_approved = queryset.filter(filter_ready_for_approval_but_not_approved())
            # From these, reported
            ready_not_approved_reported = ready_not_approved.filter(filter_sent_or_reported())
            # Approved
            approved = queryset.filter(filter_approved())
            # From these, reported
            approved_reported = approved.filter(filter_sent_or_reported())
            # Exclude approved orders
            queryset = queryset.filter(~filter_approved())
            # Slip ok but result
            slip_no_result = queryset.filter(filter_slip_no_result())
            # From these, reported
            slip_no_result_reported = slip_no_result.filter(filter_sent_or_reported())
            # No slip
            result_no_slip = queryset.filter(filter_result_no_slip())
            # From these, reported
            result_no_slip_reported = result_no_slip.filter(filter_sent_or_reported())
            # Partially finished
            partial = queryset.filter(filter_partial())
            # From these, reported
            partial_reported = partial.filter(filter_sent_or_reported())
            # Empty
            empty = queryset.filter(filter_empty() & ~filter_ready_for_approval_but_not_approved()) # AND here because orders with 0 dosimeters are in both categories
            # From these, reported
            empty_reported = empty.filter(filter_sent_or_reported())
            owner_summary = {'owner': owner,
                             'total_orders': total_orders,
                             'canceled_orders': canceled_orders.distinct().count(),
                             'ready_not_approved': ready_not_approved.distinct().count(),
                             'ready_not_approved_reported': ready_not_approved_reported.distinct().count(),
                             'approved': approved.distinct().count(),
                             'approved_reported': approved_reported.distinct().count(),
                             'slip_no_result': slip_no_result.distinct().count(),
                             'result_no_slip': result_no_slip.distinct().count(),
                             'partial': partial.distinct().count(),
                             'empty': empty.distinct().count(),
                             'slip_no_result_reported': slip_no_result_reported.distinct().count(),
                             'result_no_slip_reported': result_no_slip_reported.distinct().count(),
                             'partial_reported': partial_reported.distinct().count(),
                             'empty_reported': empty_reported.distinct().count()}
            context['owners_summary'].append(owner_summary)
        return context