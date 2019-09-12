# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
from django.utils import timezone
from oscar.apps.offer.custom import create_benefit
from oscar.apps.offer.custom import create_condition
from oscar.core.loading import get_model

Benefit = get_model('offer', 'Benefit')
Condition = get_model('offer', 'Condition')
ConditionalOffer = get_model('offer', 'ConditionalOffer')
DosimeterBenefit = get_model('offer', 'DosimeterBenefit')
DosimeterCondition = get_model('offer', 'DosimeterCondition')


class Command(BaseCommand):
    help = "Init offers."

    def handle(self, *args, **options):
        # Initialize custom conditions.
        # =====================================================================
        if not Condition.objects.filter(
                proxy_class='offer.conditions.DosimeterCondition').exists():
            create_condition(
                DosimeterCondition,
                range_id=4)
            self.stdout.write(self.style.SUCCESS(
                '`DosimeterCondition` successfully loaded.'))

        # Initialize custom benefits.
        # =====================================================================
        if not Benefit.objects.filter(
                proxy_class='offer.benefits.DosimeterBenefit').exists():
            create_benefit(
                DosimeterBenefit,
                type=DosimeterBenefit.PERCENTAGE,
                range_id=4)
            self.stdout.write(self.style.SUCCESS(
                '`DosimeterBenefit` successfully loaded.'))

        # Initialize custom conditional offer.
        # =====================================================================
        obj, created = ConditionalOffer.objects.get_or_create(
            slug='dosimeters',
            defaults={
                'name': 'Dosimeters',
                'description': 'Offer for dosimeters.',
                'offer_type': ConditionalOffer.SITE,
                'status': ConditionalOffer.OPEN,
                'condition_id': 1,
                'benefit_id': 1,
                'start_datetime': timezone.now()})

        if created:
            self.stdout.write(self.style.SUCCESS(
                '`ConditionalOffer` successfully loaded.'))
