from django.test import TestCase
from django.urls import reverse

from url_shortener.models import ShortenedURL
from url_shortener.models import generate_nice_token, make_short_url_id

class ShortenedURLTestCase(TestCase):
    def setUp(self):
        pass

    def test_token_creation(self):
        """Test that tokens don't use bad characters"""
        for i in range(100):
            token = generate_nice_token(4)
            self.assertFalse('o' in token)
            self.assertFalse('O' in token)
            self.assertFalse('i' in token)
            self.assertFalse('I' in token)
            self.assertFalse('l' in token)
            self.assertFalse('1' in token)
            self.assertFalse('0' in token)
            self.assertFalse('-' in token)
            self.assertFalse('_' in token)

    def test_url_shortening(self):
        """Test that url shortening works"""
        url_1 = 'https://example.com/instructions/111'
        short_id_1 = make_short_url_id(url_1)
        response = self.client.get(reverse('url_shortener:short_url', kwargs={'short_id': short_id_1}))
        self.assertRedirects(response, url_1, fetch_redirect_response=False)

        url_2 = 'https://example.com/reports/222'
        short_id_2 = make_short_url_id(url_2)
        response = self.client.get(reverse('url_shortener:short_url', kwargs={'short_id': short_id_2}))
        self.assertRedirects(response, url_2, fetch_redirect_response=False)

        self.assertNotEqual(short_id_1, short_id_2)