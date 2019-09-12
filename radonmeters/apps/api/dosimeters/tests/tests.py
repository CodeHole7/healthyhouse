from unittest import skipIf

from constance import config
from constance.test import override_config
from django.conf import settings
from django.core import mail
from django.test import override_settings
from oscar.core.loading import get_model
from oscar.test.factories.customer import UserFactory
from oscar.test.factories.order import OrderFactory
from oscar.test.factories.order import OrderLineFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from catalogue.tests.factories import DosimeterFactory
from owners.tests.factories import OwnerFactory, OwnerEmailConfigFactory

Dosimeter = get_model('catalogue', 'Dosimeter')


class UpdateDosimeterByLabAPITestCase(APITestCase):

    def setUp(self):
        super().setUp()

        self.admin = UserFactory(is_superuser=True, is_staff=True)
        self.laboratory = UserFactory(is_laboratory=True)
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.dosimeter_1 = DosimeterFactory(
            line=OrderLineFactory(order=OrderFactory(user=self.user1)))
        self.dosimeter_2 = DosimeterFactory(
            line=OrderLineFactory(order=OrderFactory(user=self.user2)))

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @override_config(DOSIMETERS_MANUAL_NOTIFICATIONS=False)
    def test_set_dosimeters_results_by_lab(self):
        self.client.force_login(user=self.laboratory)

        url = reverse('api:dosimeters:set_dosimeters_results_by_lab')

        data = [
            {
                "id": self.dosimeter_1.serial_number,
                "concentration": 39.1,
                "uncertainty": 13.5
            },
            {
                "id": self.dosimeter_2.serial_number,
                "concentration": 49.8,
                "uncertainty": 5.2
            },
        ]

        dosimeter_1 = Dosimeter.objects.get(serial_number=data[0]['id'])
        dosimeter_2 = Dosimeter.objects.get(serial_number=data[1]['id'])

        self.assertEqual(dosimeter_1.concentration, None)
        self.assertEqual(dosimeter_1.uncertainty, None)
        self.assertEqual(dosimeter_1.status, Dosimeter.STATUS_CHOICES.unknown)

        self.assertEqual(dosimeter_2.concentration, None)
        self.assertEqual(dosimeter_2.uncertainty, None)
        self.assertEqual(dosimeter_2.status, Dosimeter.STATUS_CHOICES.unknown)

        response = self.client.post(url,  data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dosimeter_1.refresh_from_db()
        dosimeter_2.refresh_from_db()

        self.assertEqual(dosimeter_1.concentration, data[0]['concentration'])
        self.assertEqual(dosimeter_1.uncertainty, data[0]['uncertainty'])
        self.assertEqual(dosimeter_1.status, Dosimeter.STATUS_CHOICES.completed)
        self.assertTrue(dosimeter_1.pdf_report_can_be_generated)

        self.assertEqual(dosimeter_2.concentration, data[1]['concentration'])
        self.assertEqual(dosimeter_2.uncertainty, data[1]['uncertainty'])
        self.assertEqual(dosimeter_2.status, Dosimeter.STATUS_CHOICES.completed)
        self.assertTrue(dosimeter_2.pdf_report_can_be_generated)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @override_config(DOSIMETERS_MANUAL_NOTIFICATIONS=False)
    def test_set_dosimeters_results_by_lab_owner_from_email(self):
        self.client.force_login(user=self.laboratory)

        url = reverse('api:dosimeters:set_dosimeters_results_by_lab')

        owner_config = OwnerEmailConfigFactory(from_email='owner@email.com')
        owner = owner_config.owner
        self.dosimeter_1.line.order.owner = owner
        self.dosimeter_1.line.order.save()

        data = [
            {
                "id": self.dosimeter_1.serial_number,
                "concentration": 39.1,
                "uncertainty": 13.5
            },
        ]

        dosimeter_1 = Dosimeter.objects.get(serial_number=data[0]['id'])

        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dosimeter_1.refresh_from_db()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [dosimeter_1.line.order.user.email])
        self.assertEqual(mail.outbox[0].from_email, owner_config.from_email)

    def test_set_dosimeter_status(self):
        self.client.force_login(user=self.admin)

        serial_number = '555'
        dosimeter_3 = DosimeterFactory(
            line=OrderLineFactory(order=OrderFactory(user=self.user2)),
            status=Dosimeter.STATUS_CHOICES.on_client_side,
            serial_number=serial_number)

        url = reverse('api:dosimeters:set_dosimeter_status')
        data = {"serial_number": serial_number}

        response = self.client.post(url, data=data, format='json')
        dosimeter_3.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dosimeter_3.status, Dosimeter.STATUS_CHOICES.on_store_side)

    @skipIf(True, 'Relate to translations')
    @override_settings(CELERY_ALWAYS_EAGER=True)
    @override_config(DOSIMETERS_MANUAL_NOTIFICATIONS=False)
    def test_set_dosimeters_results_by_lab_with_language(self):
        self.client.force_login(user=self.laboratory)

        url = reverse('api:dosimeters:set_dosimeters_results_by_lab')

        # TODO remove hardcode
        t_en = 'Dosimeters updates.'
        t_da = 'Dosimeter opdateringer'

        data = {
            "id": self.dosimeter_1.serial_number,
            "concentration": 39.1,
            "uncertainty": 13.5,
            "language": 'da'
        }

        # empty post
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, t_da)

        data['language'] = 'en'
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, t_en)

        del data['language']

        config.DOSIMETERS_REPORT_LANGUAGE = 'en'

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[2].subject, t_en)

        config.DOSIMETERS_REPORT_LANGUAGE = 'da'
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 4)
        self.assertEqual(mail.outbox[3].subject, t_da)


class DosimeterByAdminAPITestCase(APITestCase):

    def setUp(self):
        super().setUp()

        self.admin = UserFactory(is_superuser=True, is_staff=True)
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.dosimeter_1 = DosimeterFactory(
            line=OrderLineFactory(order=OrderFactory(user=self.user1)))
        self.dosimeter_2 = DosimeterFactory(
            line=OrderLineFactory(order=OrderFactory(user=self.user2)))

        self.url_d_1_detail = reverse('api:dosimeters:dosimeter-detail', kwargs={'pk': self.dosimeter_1.pk})

    def test_update_dosimeter(self):
        self.client.force_login(user=self.admin)

        dosimeter_1 = Dosimeter.objects.get(id=self.dosimeter_1.pk)
        self.assertEqual(dosimeter_1.concentration, None)
        self.assertEqual(dosimeter_1.uncertainty, None)
        self.assertEqual(dosimeter_1.status, Dosimeter.STATUS_CHOICES.unknown)
        self.assertEqual(dosimeter_1.use_raw_concentration, False)
        self.assertEqual(dosimeter_1.is_active, True)

        data = {
            "concentration": 39.1,
            "uncertainty": 13.5,
            'use_raw_concentration': True,
            'is_active': False
        }
        response = self.client.patch(self.url_d_1_detail,  data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dosimeter_1.refresh_from_db()

        self.assertEqual(dosimeter_1.concentration, data['concentration'])
        self.assertEqual(dosimeter_1.uncertainty, data['uncertainty'])
        self.assertEqual(dosimeter_1.status, Dosimeter.STATUS_CHOICES.unknown)
        self.assertTrue(dosimeter_1.pdf_report_can_be_generated)
        self.assertEqual(dosimeter_1.use_raw_concentration, True)
        self.assertEqual(dosimeter_1.is_active, False)

    def test_update_active_area(self):
        self.client.force_login(user=self.admin)

        dosimeter_1 = Dosimeter.objects.get(id=self.dosimeter_1.pk)
        self.assertEqual(dosimeter_1.active_area, True)

        data = {"active_area": False}
        response = self.client.patch(self.url_d_1_detail,  data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dosimeter_1.refresh_from_db()

        self.assertEqual(dosimeter_1.active_area, False)

    def test_dosimeter_detail(self):
        self.client.force_login(user=self.admin)

        url = reverse('api:dosimeters:dosimeter-detail', kwargs={'pk': self.dosimeter_1.pk})

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dosimeter_1 = Dosimeter.objects.get(id=self.dosimeter_1.pk)
        expected_data = {
            'status': dosimeter_1.status,
            'serial_number': dosimeter_1.serial_number,

            'concentration_visual': dosimeter_1.concentration_visual,
            'uncertainty_visual': dosimeter_1.uncertainty_visual,
            'avg_concentration_visual': dosimeter_1.avg_concentration_visual,
            'active_area': dosimeter_1.active_area,
            'is_active': True,
            'use_raw_concentration': dosimeter_1.use_raw_concentration,

            'concentration': dosimeter_1.concentration,
            'uncertainty': dosimeter_1.uncertainty,
            'measurement_start_date': dosimeter_1.measurement_start_date.strftime(settings.DATE_FORMAT_REST),
            'measurement_end_date': dosimeter_1.measurement_end_date.strftime(settings.DATE_FORMAT_REST),
            'floor': dosimeter_1.floor,
            'location': dosimeter_1.location,
        }
        self.assertEqual(response.data, expected_data)
