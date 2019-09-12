
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from deliveries.forms import UpdateDosimeterStatusRequestForm
from django.urls import reverse_lazy
from oscar.core.loading import get_model
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from deliveries.utils import _return_pdf, _generate_reports_pdf
from django.http import HttpResponse, HttpResponseNotFound


Dosimeter = get_model('catalogue', 'Dosimeter')
Order = get_model('order', 'Order')
OrderLine = get_model('order','Line')

"""
	@author: alex m
	@created: 2019.8.27
	@desc: user updates dosimeter's status to 'ready_for_packaging'
"""

class DosimeterStatusUpdateView(FormView):
	"""docstring for DosimeterStatusUpdate"""
	template_name = 'deliveries/dosimeter_update.html'
	
	form_class = UpdateDosimeterStatusRequestForm

	def get_form_kwargs(self):

		kwargs = super().get_form_kwargs()
		kwargs['user_id'] = self.request.user.id
		return kwargs
	
	def form_valid(self, form):

		messages.success(self.request, _('Your Dosimeter status successfully updated.'))
		form.update_dosimeter_status()
		self.success_url = reverse_lazy('deliveries:download_dosimeter_reports_pdf', args=[self.request.POST.get('serial_number')])
		return super().form_valid(form)

	# def get_context_data(self, **kwargs):
	# 	context = super().get_context_data(**kwargs)
	# 	if context['serial_number']:
	# 		context['down_pdf'] = reverse_lazy('deliveries:download_dosimeter_reportspdf', args=[self.kwargs['serial_number']])
	# 	return context


@require_http_methods(["GET"])
def download_dosimeter_reports_pdf(request, serial_number):
	if serial_number is not None:
		try:
			dosimeter = Dosimeter.objects.get(serial_number = serial_number)	
			dataset = _generate_reports_pdf(dosimeter)
			return _return_pdf(dataset[0])
		except Dosimeter.DoesNotExist:		
			pass
		finally:
			pass
	return HttpResponseNotFound('<h1>Invalid Number</h1>')