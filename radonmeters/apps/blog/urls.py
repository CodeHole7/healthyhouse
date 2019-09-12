# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url

from blog.views import EntryDetailView

urlpatterns = [
    url(r'^blog/(?P<pk>\d+)/$', EntryDetailView.as_view(), name='blog_entry_detail'),
    url(r'^blog/', include('zinnia.urls')),
    url(r'^comments/', include('django_comments.urls')),
]
