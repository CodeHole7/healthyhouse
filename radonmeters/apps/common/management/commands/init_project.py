# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
from django.core.management import CommandError
from django.core.management import call_command
from django.db import IntegrityError
from oscar.apps.address.models import Country
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.apps.partner.models import Partner
from oscar.core.compat import get_user_model

from catalogue.models import Category
from catalogue.models import ProductAttribute
from catalogue.models import ProductClass


class Command(BaseCommand):
    help = "Init structure of pages, categories, products."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing has been started.'))

        # Initialize migrations.
        # =====================================================================
        call_command('migrate')

        # Initialize countries.
        # =====================================================================
        try:
            call_command('oscar_populate_countries', '--no-shipping')
            Country.objects.filter(
                iso_3166_1_a2='DK').update(is_shipping_country=True)
        except CommandError:
            self.stdout.write(self.style.WARNING(
                'You already have countries in your database.'))

        # Try to create superuser.
        # =====================================================================
        try:
            get_user_model().objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin')
            self.stdout.write(self.style.SUCCESS('Superuser successfully loaded.'))
        except IntegrityError:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))

        # Initialize categories.
        # =====================================================================
        categories = (
            'RADON > ANALOG DEVICES',
            'RADON > ELECTRONIC DEVICES',
            'MOLD > PRODUCTS',
            'HOME ACCESSORIES > PRODUCTS')

        for breadcrumbs in categories:
            create_from_breadcrumbs(breadcrumbs)

        lorem = """
            <p>
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. 
            Consequuntur nam nesciunt sapiente veniam voluptatum! 
            Aperiam architecto aut beatae consequatur cumque delectus earum 
            laborum, nesciunt nisi numquam, officia tempora unde voluptatibus.
            </p>
            """

        Category.objects.filter(depth=1).update(description=lorem)

        self.stdout.write(self.style.SUCCESS('Categories successfully loaded.'))

        # Initialize category sections.
        # =====================================================================
        call_command('loaddata', 'fixtures/category_sections.json')
        self.stdout.write(self.style.SUCCESS(
            'Category sections successfully loaded.'))

        # Initialize default product class.
        # =====================================================================
        product_cls, created = ProductClass.objects.update_or_create(
            name='Default',
            slug='default')
        ProductAttribute.objects.update_or_create(
            product_class=product_cls,
            code='promo_image',
            name='Promotion Image',
            type=ProductAttribute.IMAGE)
        self.stdout.write(self.style.SUCCESS(
            'Default product successfully loaded.'))

        # Initialize default partner.
        # =====================================================================
        try:
            Partner.objects.create(
                name='Default',
                code='default')
        except IntegrityError:
            self.stdout.write(self.style.WARNING(
                'Default partner already exists.'))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Default partner was successfully loaded.'))

        # Initialize products.
        # =====================================================================
        call_command('loaddata', 'fixtures/products.json')
        self.stdout.write(self.style.SUCCESS('Products were successfully loaded.'))

        # Initialize ranges.
        # =====================================================================
        call_command('loaddata', 'fixtures/ranges.json')
        self.stdout.write(self.style.SUCCESS('Ranges were successfully loaded.'))

        # Initialize flatpages.
        # =====================================================================
        call_command('loaddata', 'fixtures/flatpages.json')
        self.stdout.write(self.style.SUCCESS('Flatpages were successfully loaded.'))

        # Initialize promotions.
        # =====================================================================
        call_command('loaddata', 'fixtures/promotions.json')
        self.stdout.write(self.style.SUCCESS('Promotions were successfully loaded.'))

        # Initialize webblog.
        # =====================================================================
        call_command('loaddata', 'fixtures/webblog_categories.json')
        call_command('loaddata', 'fixtures/webblog_entries.json')
        self.stdout.write(self.style.SUCCESS('WebBlog was successfully loaded.'))

        # Initialize payment app.
        # =====================================================================
        call_command('loaddata', 'fixtures/payment_source_types.json')
        self.stdout.write(self.style.SUCCESS('Payment app was successfully loaded.'))

        # Initialize custom conditions and benefits.
        # =====================================================================
        call_command('init_offers')

        # Initialize locations.
        # =====================================================================
        call_command('loaddata', 'locations.json')
        self.stdout.write(self.style.SUCCESS(
            'Locations were successfully loaded.'))

        self.stdout.write(self.style.SUCCESS('Initializing has been ended.'))
