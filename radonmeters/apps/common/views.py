# -*- coding: utf-8 -*-
import requests
from constance import config
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404
from django.http.response import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic import View
from django.views.generic.edit import CreateView
from functools import wraps
from oscar.apps.promotions.models import RawHTML
from oscar.core.loading import get_model
from zinnia.models.entry import Entry

from common.forms import ConsultationRequestForm
from common.forms import ContactUsRequestForm
from common.forms import SubscribeRequestForm
from common.models import CategorySection
from common.utils import is_radosure

Range = get_model('offer', 'Range')
Category = get_model('catalogue', 'Category')


class HealthCheckView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(settings.HEALTH_CHECK_BODY, status=200)


class HomeView(TemplateView):
    """
    This is the home page and will typically live at /
    """
    template_name = 'layout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add `slider`.
        slider_range = Range.objects.filter(slug='home_page_slider').first()
        if slider_range:
            context['slider'] = slider_range.included_products.all()

        # Add `our_top_products`.
        products_range = Range.objects.filter(slug='our_top_products').first()
        if products_range:
            context['our_top_products'] = products_range.included_products.all()

        # Add `our_advantages_text`.
        our_advantages = RawHTML.objects.filter(
            name='home_page_our_advantages').first()
        if our_advantages:
            context['our_advantages_text'] = our_advantages.body

        # Add `latest_articles`.
        context['latest_articles'] = Entry.published.on_site()[:3]

        return context

    def get(self, request, *args, **kwargs):
        if is_radosure():
            # for radosure redirect to orders page.
            url = reverse('dashboard:order-list')
            return redirect(url)
        return super().get(request, *args, **kwargs)


class PromoRadonView(TemplateView):
    """
    Template view for representation promo page of Radon.
    """

    template_name = 'common/promo_radon.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add instance of Category model.
        try:
            context['category'] = Category.objects.get(name__iexact='radon')
        except ObjectDoesNotExist:
            raise Http404

        # Add related instances of CategorySection model.
        context['category_sections'] = CategorySection.objects.filter(
            category=context['category'])

        # Add related instances of Entry model.
        context['related_entries'] = Entry.published.on_site().filter(
            categories__title__iexact=context['category'].name)[:3]

        return context


class SubscribeRequestView(CreateView):
    form_class = SubscribeRequestForm
    http_method_names = ('post', )
    template_name = 'base.html'

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            return super().post(request, *args, **kwargs)
        else:
            raise Http404

    def form_valid(self, form):
        self.object = form.save()
        data = {'message': _('Email has been added into subscribe list.')}
        return JsonResponse(data=data, status=201)

    def form_invalid(self, form):
        data = {'errors': form.errors}
        return JsonResponse(data=data, status=400)


class ConsultationRequestView(CreateView):
    form_class = ConsultationRequestForm
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            return super().post(request, *args, **kwargs)
        else:
            raise Http404

    def form_valid(self, form):
        self.object = form.save()
        data = {'message': _('Consultation request has been created.')}
        return JsonResponse(data=data, status=201)

    def form_invalid(self, form):
        data = {'errors': form.errors}
        return JsonResponse(data=data, status=400)


def check_recaptcha(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        request.recaptcha_is_valid = None
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': config.SERVICES_GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post(settings.SERVICES_GOOGLE_RECAPTCHA_VERIFY_URL, data=data)
            result = r.json()
            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        return view_func(self, request, *args, **kwargs)
    return _wrapped_view


class ContactUsRequestView(CreateView):
    form_class = ContactUsRequestForm
    template_name = 'common/contact_us.html'
    success_url = reverse_lazy('common:contact_us_request')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _('Your message successfully sent.'))
        return super().form_valid(form)

    @check_recaptcha
    def post(self, request, *args, **kwargs):
        self.object = None

        form = self.get_form()
        if form.is_valid():
            if request.recaptcha_is_valid:
                return self.form_valid(form)
            else:
                return self.render_to_response(self.get_context_data(form=form))
        else:
            return self.form_invalid(form)
