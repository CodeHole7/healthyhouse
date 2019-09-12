import math
import re
import secrets

import django.db.models as models

REGEX_NICE = re.compile('[-_0oO1liI]+')
RETRY_COUNT = 1000
TOKEN_DEFAULT_SIZE = 6

class ShortenedURL(models.Model):
    """
    Model for storing short IDs for long urls.
    """

    original_url = models.URLField(unique=True)
    short_id = models.CharField(max_length=10, unique=True)

    def short_url(self):
        return 

def generate_nice_token(size):
    """Generate alphanumerical random token that does not contain 1, l, i, I, o, O, 0 characters.

    ``size`` is a minimal number of characters in the token.
    """
    while True:
        token = secrets.token_urlsafe(math.ceil(size*3/2))[:-size]
        if not REGEX_NICE.search(token):
            return token

def generate_unique_token(size):
    """Generate token such that it's not in database.

    ``size`` is a minimal number of characters in the token.
    """
    try_counter = 0
    while try_counter < RETRY_COUNT:
        token = generate_nice_token(size)
        try:
            ShortenedURL.objects.get(short_id=token)
        except ShortenedURL.DoesNotExist:
            return token
        try_counter += 1
    return generate_unique_token(size+1)

def make_short_url_id(url):
    """Get or create short url id for the given url and return it.

    This also creates a record in a database for redirection to work.
    """
    try:
        return ShortenedURL.objects.get(original_url=url).short_id
    except ShortenedURL.DoesNotExist:
        short_id = generate_unique_token(TOKEN_DEFAULT_SIZE)
    ShortenedURL.objects.create(original_url=url, short_id=short_id)
    return short_id