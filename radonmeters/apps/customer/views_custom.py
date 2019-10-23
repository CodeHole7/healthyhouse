from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from instructions.models import Instruction


class InstructionDetailView(generic.ListView):
    """
    Brand new classes for orders page
    View for anonymous users.
    It looks like OrderHistoryView for signed
    """

    context_object_name = "orders"
    template_name = 'customer/order/order_list_instruction.html'
    paginate_by = settings.OSCAR_ORDERS_PER_PAGE
    instruction = None
    pk_url_kwarg = 'pk'

    def get(self, request, *args, **kwargs):
        self.instruction = self.get_object()
        self.object_list = self.get_queryset()
        for order in self.object_list:
            for line in order.lines.all():
                for dosimeter in line.dosimeters.filter(measurement_start_date__isnull=True):
                    dosimeter.measurement_start_date = timezone.now()
                    dosimeter.save()
                    messages.success(
                        request=self.request,
                        message=_('Measurement start time for dosimeter "%s" has been successfully updated to current date.') % dosimeter.serial_number)
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            # Get the single item from the filtered queryset
            instruction = Instruction.objects.get(pk=pk)
        except Instruction.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': Instruction._meta.verbose_name})

        return instruction

    def get_queryset(self):
        return self.instruction.orders.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.instruction
        return context
