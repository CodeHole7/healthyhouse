from django.conf import settings
from django.contrib import messages
from django.urls.base import reverse
from django.utils.translation import ugettext as _
from django.views import generic
from oscar.views import sort_queryset

from catalogue.models import Dosimeter, Batch, Batch_Dosimeter
from dashboard.dosimeters.forms import DosimeterDashboardChangeForm
from dashboard.dosimeters.forms import DosimeterDashboardSearchForm
from dashboard.dosimeters.forms import DosimeterDashboardUpdateForm
from dashboard.dosimeters.forms import BatchSelectDashboardUpdateForm
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponse, HttpResponseNotFound
import os
from django.shortcuts import redirect
from owners.models import Owner

from django.core.mail import send_mail
from django.core.mail import get_connection

class DosimeterDashboardListView(generic.ListView):
    """
    View for representation dosimeters in the Oscar's Dashboard.
    """

    # It's taken from default realisation for
    # the same functionality (partners app).

    model = Dosimeter
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
    form_class = DosimeterDashboardSearchForm
    form_update_class = DosimeterDashboardUpdateForm
    context_object_name = 'dosimeters'
    template_name = 'dashboard/dosimeters/dosimeter_list.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form = None
        self.description = None
        self.is_filtered = None

    def get_queryset(self):
        qs = self.model._default_manager.all()
        qs = sort_queryset(qs, self.request, ['-created'])
        qs = qs.select_related('line__order')

        self.description = _("All dosimeters")

        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        self.form_update = self.form_update_class()
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['id']:
            qs = qs.filter(id=data['id'])
            self.description = _("Dosimeters matching '%s'") % data['id']
            self.is_filtered = True

        if data['serial_number']:
            qs = qs.filter(serial_number=data['serial_number'])
            self.description = _("Dosimeters matching '%s'") % data['serial_number']
            self.is_filtered = True

        if data['order_number']:
            qs = qs.filter(line__order__number=data['order_number'])
            self.description = _("Dosimeters matching '%s'") % data['order_number']
            self.is_filtered = True

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['form_update'] = self.form_update
        context['is_filtered'] = self.is_filtered
        context['queryset_description'] = self.description
        #context['auto_down_pdf'] = None
        return context


    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        self.form_update = self.form_update_class(self.request.POST)
        self.updated_dosimeter = ''
        auto_down_pdf = None
        if self.form_update.is_valid():
            data = self.form_update.cleaned_data

            try:
                dosimeter = self.object_list.get(serial_number=data['serial_number'])
                self.is_filtered = True
                order_number = dosimeter.line.order.number
                self.object_list = self.object_list.filter(line__order__number=order_number)
                self.description = _("All dosimeters for the order '%s'") % order_number
                if dosimeter.status != data['status']:
                    # redirect to batch creator
                    if data['status'] == Dosimeter.STATUS_CHOICES.shipped_to_distributor:
                        return redirect('dashboard:dosimeter-batch', serial_number=data['serial_number'], owner = data['owner'], status=data['status'])

                    dosimeter.status = data['status']
                    # pending code
                    #dosimeter.line.order.owner_id = data['owner']
                    #dosimeter.line.order.save()
                    # -----------
                    dosimeter.save()
                    if data['status'] == Dosimeter.STATUS_CHOICES.ready_for_packaging:
                        # generated a report pdf and automatically send it to customer
                        pdf_path =  dosimeter.dosimeter_pdf_report_generate()
                        auto_down_pdf = data['serial_number']
                    if data['status'] == Dosimeter.STATUS_CHOICES.recieved_from_distributor:
                        # check if all dosimeters are recieved_from_distributor
                        batch_dosimeter = Batch_Dosimeter.objects.get(dosimeter_id = dosimeter.id)
                        batch = batch_dosimeter.batch
                        batch_id = batch.id
                        owner = batch.batch_owner
                        bds = Batch_Dosimeter.objects.all().filter(batch_id = batch_id)
                        email = False
                        email_content = 'Here are dosimeters \n'
                        total_count = 0
                        for bd in bds:
                            if bd.dosimeter.status == Dosimeter.STATUS_CHOICES.recieved_from_distributor:
                                email = True                                
                                email_content = email_content + bd.dosimeter.serial_number + '\n'
                                total_count = total_count + 1
                            else:
                                email = False
                                break
                        if email:
                            #sending email to owner
                            email_content = email_content + 'Totals: %s' % str(total_count)

                            send_mail(
                                'All Dosimeters are arrived successfully',
                                email_content,
                                'baduki@livecheats.net',
                                [owner.email],
                                fail_silently=True,
                            )

                            messages.success(
                            request=self.request,
                            message=_('Just sent email to owner because all dosimeters in "%s" batch are received from "%s" owner') % \
                                (batch.batch_name,owner.first_name))

                    self.updated_dosimeter = data['serial_number']
                    messages.success(
                        request=self.request,
                        message=_('Dosimeter "%s" has been successfully updated.') % data['serial_number'])
                    if Dosimeter.objects.filter(is_active=True, line__order_id=dosimeter.line.order.id).count() == 0:
                        messages.warning(
                        request=self.request,
                        message=_('All dosimeters in order "%s" are inactive.') % order_number)
                    else:
                        if dosimeter.line.order.scan_dosimeters():
                            messages.success(
                                request=self.request,
                                message=_('An e-mail for order "%s" has been sent.') % order_number)
                else:
                    messages.warning(
                        request=self.request,
                        message=_('Dosimeter "%s" cannot be updated because it already has "%s" state.') % (data['serial_number'], data['status']))
            except Dosimeter.DoesNotExist:
                messages.error(
                    request=self.request,
                    message=_('Dosimeter "%s" cannot be found.') % data['serial_number'])
            except Dosimeter.MultipleObjectsReturned:
                messages.error(
                    request=self.request,
                    message=_('Serial number "%s" is used by several dosimeters!') % data['serial_number'])
        #self.form_update = self.form_update_class(initial={'status': self.form_update.data['status']})
        context = self.get_context_data()
        context['updated_dosimeter'] = self.updated_dosimeter

        if auto_down_pdf is not None:
            context['auto_down_pdf'] = './download-dosimeter-reports-pdf/%s'%auto_down_pdf
        return self.render_to_response(context)

    
class DownloadDosimeterReportPDF(View):

    def get(self, request, serial_number, *args, **kwargs):
        if serial_number is not None:
                file_path = os.path.join('./radonmeters/static', "dosimeter_pdf/%s.pdf"%serial_number)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as fh:
                        response = HttpResponse(fh.read(), content_type="application/pdf")
                        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                        return response
                
        return HttpResponseNotFound('<h1>Invalid Number</h1>')

class BatchSelectDashboardView(generic.TemplateView):
    template_name = 'dashboard/dosimeters/dosimeter_batch.html'
    
    form_update_class = BatchSelectDashboardUpdateForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context

    def get(self, request, serial_number, owner, status, *args, **kwargs):

        owner_object = Owner.objects.get(id=owner)

        context = self.get_context_data()
        context['info_data'] = {'serial_number':serial_number,'owner':owner_object.first_name,'status':status}

        self.form_update = self.form_update_class(
            initial={'serial_number':serial_number,'owner':owner,'status':status}            
        )
        #self.form_update.set_batchs(owner)
        
        context['form_update'] =self.form_update
        return self.render_to_response(context)

        #return HttpResponseNotFound("<h1>Invalid Parameters</h1>")
        #return HttpResponseNotFound("<h1>Invalid Request</h1>")
    def post(self, request,serial_number, owner, status, *args, **kwargs):
        
        owner_object = Owner.objects.get(id=owner)

        context = self.get_context_data()

        context['info_data'] = {'serial_number':serial_number,'owner':owner_object.first_name,'status':status}        

        self.form_update = self.form_update_class(request.POST, initial={'owner':request.POST.get('owner')})
        #self.form_update.set_batchs(request.POST.get('batchs'))

        if self.form_update.is_valid():
            batch = self.form_update.save_data()          
            messages.success(
                        request=self.request,
                        message=_('Dosimeter "%s" status is changed "%s" successfully, and included batch "%s"') % \
                        (serial_number, status, batch.batch_name))
            return redirect('dashboard:dosimeter-list')
        context['form_update'] = self.form_update

        return self.render_to_response(context)

class DosimeterDashboardUpdateView(generic.UpdateView):
    """
    View for updating dosimeters in the Oscar's Dashboard.
    """

    model = Dosimeter
    form_class = DosimeterDashboardChangeForm
    context_object_name = 'dosimeter'
    template_name = 'dashboard/dosimeters/dosimeter_detail.html'

    def get_success_url(self):
        next_url = self.request.POST.get('next_url')
        if next_url:
            return next_url
        else:
            return reverse('dashboard:dosimeter-list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.previous_status = self.object.status
        result = super().post(request, *args, **kwargs)
        if self.object.status != self.previous_status:
            if Dosimeter.objects.filter(is_active=True, line__order_id=self.object.line.order.id).count() == 0:
                        messages.warning(
                        request=self.request,
                        message=_('All dosimeters in order "%s" are inactive.') % self.object.line.order.number)
            else:
                if self.object.line.order.scan_dosimeters():
                    messages.success(
                        request=self.request,
                        message=_('An e-mail for order "%s" has been sent.') % self.object.line.order.number)
        return result

    def form_valid(self, form):
        # Create success message for admin.
        messages.success(
            request=self.request,
            message=_('Dosimeter "%s" has been successfully updated.') % self.object.id)

        # Return to default behavior for `form_valid`.
        return super().form_valid(form)
