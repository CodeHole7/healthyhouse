# -*- coding: utf-8 -*-
from constance import config
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Init service keys."

    def handle(self, *args, **options):
        default_keys = settings.DEFAULT_SERVICES

        messages = []
        google_key = default_keys.get('GOOGLE_KEY')
        if not config.SERVICES_GOOGLE_KEY and google_key:
            config.SERVICES_GOOGLE_KEY = google_key
            messages.append('Google key has been created.')

        retur_link = default_keys.get('RETUR_LINK')
        if not config.SERVICES_RETUR_LINK and retur_link:
            config.SERVICES_RETUR_LINK = retur_link
            messages.append('Retur link has been created.')
            
        trust_template_id = default_keys.get('TRUSTPILOT_TEMPLATE_ID')
        trust_business_id = default_keys.get('TRUSTPILOT_BUSINESSUNIT_ID')
        trust_link = default_keys.get('TRUSTPILOT_LINK')

        if not config.SERVICES_TRUSTPILOT_TEMPLATE_ID and trust_template_id:
            config.SERVICES_TRUSTPILOT_TEMPLATE_ID = trust_template_id
            messages.append('Trust pilot template id has been created.')

        if not config.SERVICES_TRUSTPILOT_LINK and trust_link:
            config.SERVICES_TRUSTPILOT_LINK = trust_link
            messages.append('Trust pilot link has been created.')

        if not config.SERVICES_TRUSTPILOT_BUSINESSUNIT_ID and trust_business_id:
            config.SERVICES_TRUSTPILOT_BUSINESSUNIT_ID = trust_business_id
            messages.append('Trust pilot business unit id has been created.')

        if not messages:
            self.stdout.write(self.style.ERROR(
                'All variables was changed previously.'))
        else:
            for m in messages:
                self.stdout.write(self.style.SUCCESS(m))
