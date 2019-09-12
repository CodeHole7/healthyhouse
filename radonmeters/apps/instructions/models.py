# -*- coding: utf-8 -*-
import uuid

from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from oscar.core.compat import AUTH_USER_MODEL
from oscar.core.loading import get_model
from django.template import engines

from common.models import UUIDAbstractModel
from common.utils import render_html_preview
from customer.utils import get_email_templates, COMM_TYPE_INSTRUCTION

Order = get_model('order', 'Order')


class InstructionTemplate(TimeStampedModel):
    """
    Model for instruction templates.
    """

    pdf_template = models.TextField(_('Template'))
    is_active = models.BooleanField(_('Is active?'), default=True)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return str(self.id)

    @classmethod
    def can_change_is_active(cls, instance, is_active):
        """Check if there any default instruction template"""
        if not is_active:
            qs = cls.objects.filter(is_active=True)
            if instance and instance.id:
                qs = qs.exclude(id=instance.id)
            return qs.exists()
        return True

    @classmethod
    def prepare_pdf_preview(cls, template, context, as_image=True):
        """
        Generate Instruction PDF report.

        :return: The PDF as byte string.
        """

        django_engine = engines['django']
        template = django_engine.from_string(template)

        # Prepare html for rendering to PDF.
        return render_html_preview(template, context, as_image)

    @classmethod
    def active(cls):
        return cls.objects.filter(is_active=True).first()

    def render_pdf(self, context):
        return self.prepare_pdf_preview(self.pdf_template, context, False)


class InstructionImage(models.Model):
    image = models.ImageField(
        _('Image'), upload_to='instructions/images/')

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return str(self.id)


class Instruction(UUIDAbstractModel, TimeStampedModel):
    """
    Model for instruction.
    """

    pdf_file = models.FileField(
        _('Instruction'), upload_to='instructions/pdf/')

    user = models.ForeignKey(
        AUTH_USER_MODEL, related_name='instructions', verbose_name=_("User"))
    orders = models.ManyToManyField(
        Order, verbose_name=_('Orders'))

    class Meta:
        ordering = ('-created', )

    @classmethod
    def create(cls, user, orders: list):
        template = InstructionTemplate.active()
        if template:
            instruction_id = uuid.uuid4()
            context = {
                'orders': orders,
                'customer': [user],
                'instruction_id': instruction_id
            }
            file_content = template.render_pdf(context)
            instruction = Instruction.objects.create(
                id=instruction_id,
                user=user,
            )
            file = ContentFile(file_content)
            instruction.pdf_file.save(f'instruction_{instruction.id}.pdf', file)
            instruction.orders.add(*orders)
            return instruction

        # cannot generate instruction without template
        return None

    def get_file_content(self):
        return self.pdf_file.read()

    def get_public_url(self):
        return reverse('customer:instruction-detail', args=(self.id,))

    def send_to_customer(self):
        order = self.orders.first()
        context = {
            'order': order,
            'instruction': self,
        }
        msg = order.prepare_email_msg(COMM_TYPE_INSTRUCTION, context)
        msg.attach_file(self.pdf_file.path, mimetype="application/pdf")
        msg.send()
