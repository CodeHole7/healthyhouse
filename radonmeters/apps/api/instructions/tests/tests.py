from oscar.core.loading import get_model
from oscar.test.factories.customer import UserFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api.instructions.tests.factories import InstructionFactory
from instructions.templatetags.instruction import build_instruction_link

Dosimeter = get_model('catalogue', 'Dosimeter')


class InstructionImageAPITestCase(APITestCase):

    def setUp(self):
        super().setUp()
        self.admin = UserFactory(is_superuser=True, is_staff=True)

        self.user = UserFactory()
        self.instruction = InstructionFactory(user=self.user )

    def test_instruction_link(self):
        context = {'instruction_id': self.instruction.id}
        url = build_instruction_link(context)
        expected_url = reverse(
            'customer:instruction-detail', args=(self.instruction.id,))
        self.assertEqual(url, 'http://example.com' + expected_url)

    def test_instruction_public_link(self):
        response = self.client.get(self.instruction.get_public_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
