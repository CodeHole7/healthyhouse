from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

class URLShortenerAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:url_shortener:create-short-url')

    def test_permission(self):
        response = self.client.get(self.url, {'url': 'https://example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_example_data(self):
        original_url = 'https://example.com'
        response = self.client.get(self.url, {'url': original_url})
        self.assertEqual(response.data['original_url'], original_url)
        self.assertRedirects(self.client.get(response.data['short_url']), original_url, fetch_redirect_response=False)
