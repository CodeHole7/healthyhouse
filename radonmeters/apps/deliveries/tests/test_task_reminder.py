from datetime import timedelta

from django.core import mail
from django.test import override_settings
from django.test import TestCase
from django.utils import timezone
from oscar.test.factories.customer import UserFactory
from oscar.test.factories.order import OrderFactory

from deliveries.tests.factoriees import ShipmentFactory
from deliveries.tasks import delivery_remind_pickup


@override_settings(CELERY_ALWAYS_EAGER=True)
@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class RemindShipmentTestCase(TestCase):

    def test_task(self):
        # invalid statuses
        ShipmentFactory(current_status='FAILED')
        ShipmentFactory(current_status='UNKNOWN')

        # 13 days
        ShipmentFactory(
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now())
        # 10 days
        s_10 = ShipmentFactory(
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now() - timedelta(days=3))
        # 9 days
        ShipmentFactory(
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now() - timedelta(days=4))
        # 6 days
        ShipmentFactory(
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now() - timedelta(days=7))
        # 5 days
        s_5 = ShipmentFactory(
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now() - timedelta(days=8))
        # 4 days
        ShipmentFactory(
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now() - timedelta(days=9))
        # 1 day
        order_user = OrderFactory(user=UserFactory())
        s_1 = ShipmentFactory(
            order=order_user,
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now() - timedelta(days=12))
        # negative
        ShipmentFactory(
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now() - timedelta(days=15))
        ShipmentFactory(
            current_status='AVAILABLE_FOR_DELIVERY',
            current_status_registered_at=timezone.now() - timedelta(days=20))

        delivery_remind_pickup.delay()

        self.assertEqual(len(mail.outbox), 3)

        expected_emails = {
            s_1.order.user.email,
            s_5.order.guest_email,
            s_10.order.guest_email
        }
        emails = {to for m in mail.outbox for to in m.to}
        self.assertEqual(expected_emails, emails)
