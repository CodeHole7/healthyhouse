# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from oscar.core.loading import get_model

from customer.utils import COMM_TYPES

CommunicationEventType = get_model('customer', 'CommunicationEventType')


class Command(BaseCommand):
    """
    Sync email comm types
    """

    help = 'Sync email communication types'

    def handle(self, *args, **options):
        self.stdout.write("Start syncing communication types.")

        for comm_type in COMM_TYPES:
            obj, created = CommunicationEventType.objects.get_or_create(
                code=comm_type,
                defaults={
                    'name': comm_type,
                    'category': CommunicationEventType.ORDER_RELATED,
                    'email_subject_template': get_template(COMM_TYPES[comm_type]['subject']).render(),
                    'email_body_template': get_template(COMM_TYPES[comm_type]['message']).render(),
                    'email_body_html_template': get_template(COMM_TYPES[comm_type]['html_message']).render(),
                }
            )
            if created:
                self.stdout.write("%s was created" % comm_type)
        self.stdout.write("Communication types have been synced.")
