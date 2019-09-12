from constance import config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from oscar.apps.checkout.mixins import \
    OrderPlacementMixin as CoreOrderPlacementMixin

from common.utils import create_invoice_pdf


class OrderPlacementMixin(CoreOrderPlacementMixin):

    def send_confirmation_message(self, order, code, **kwargs):
        context = self.get_message_context(order)
        context['config'] = config
        invoice_pdf = create_invoice_pdf(order, context)

        subject = _('Invoice')
        from_email = settings.DEFAULT_FROM_EMAIL
        to = order.user.email
        text_content = render_to_string(
            'customer/emails/commtype_order_placed_body.txt',
            context=context)
        html_content = render_to_string(
            'customer/emails/commtype_order_placed_body.html',
            context=context)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.attach_file(invoice_pdf)
        msg.send()
