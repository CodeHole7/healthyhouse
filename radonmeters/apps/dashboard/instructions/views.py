from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.urls.base import reverse_lazy
from django.views import generic
from django.views.generic.edit import ProcessFormView, ModelFormMixin
from oscar.core.loading import get_model

from dashboard.instructions.forms import InstructionTemplateForm


Order = get_model('order', 'Order')
Instruction = get_model('instructions', 'Instruction')
InstructionImage = get_model('instructions', 'InstructionImage')
InstructionTemplate = get_model('instructions', 'InstructionTemplate')


class InstructionTemplateListView(generic.ListView):
    """
    View for representation instructions templates in the Oscar's Dashboard.
    """

    model = InstructionTemplate
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
    context_object_name = 'templates'
    template_name = 'dashboard/instructions/template_list.html'


class InstructionTemplateFormView(ModelFormMixin, ProcessFormView):
    model = InstructionTemplate
    form_class = InstructionTemplateForm
    context_object_name = 'template'
    template_name = 'dashboard/instructions/template_detail.html'
    success_url = reverse_lazy('dashboard:instruction-template-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'images': InstructionImage.objects.all()
        })
        return context

    def form_invalid(self, form):
        if 'render_preview' in self.request.POST:
            data = {'errors': form.errors}
            return JsonResponse(data=data, status=400)
        messages.error(
            self.request,
            _("The submitted form was not valid, please correct "
              "the errors and resubmit"))
        return super(InstructionTemplateFormView, self).form_invalid(form)

    def form_valid(self, form):
        if 'render_preview' in self.request.POST:
            return self.render_preview(form)
        return super(InstructionTemplateFormView, self).form_valid(form)

    def render_preview(self, form):
        form.save(commit=False)
        template = form.cleaned_data['pdf_template']
        # Prepare data.
        context = {
            'orders': [form.preview_order],
            'customer': [form.preview_order.user],
        }
        file_data = InstructionTemplate.prepare_pdf_preview(template, context, True)

        # Prepare response.
        response = HttpResponse(content_type='image/png')
        # View on the current page
        response['Content-Disposition'] = 'inline;'
        response.write(file_data)
        return response


class InstructionTemplateUpdateView(InstructionTemplateFormView, generic.UpdateView):
    pass


class InstructionTemplateCreateView(InstructionTemplateFormView, generic.CreateView):
    pass


class InstructionCreateView(generic.CreateView):
    model = Instruction

