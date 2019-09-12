from django.shortcuts import get_object_or_404, redirect

from url_shortener.models import ShortenedURL

def url_redirect(request, short_id):
    url_record = get_object_or_404(ShortenedURL, short_id=short_id)
    return redirect(url_record.original_url)