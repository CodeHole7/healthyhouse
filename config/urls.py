# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages.views import flatpage
from oscar.app import application
from rest_framework.documentation import include_docs_urls

from common.utils import is_radosure
from common.admin import RestartSupervisorView

urlpatterns = [
    # Include i18n's URLs.
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Include application's URLs.
    url(r'', include("common.urls", namespace="common")),

    # Include Oscar's URLs.
    url(r'', include(application.urls)),

    # Include API's URLs.
    url(r'^api/v1/', include('api.urls', namespace='api')),
    url(r'^api/v1/docs/', include_docs_urls(title='Radonmeters API doc')),

    # Include ckEditor's URLs.
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    # Include url shortener URLs.
    url(r'^hh/', include('url_shortener.urls', namespace="url_shortener")),
    

    # include voucher url.
    # url(r'voucher/', include('voucher.urls', namespace='voucher')),

    # The Django admin is not officially supported; expect breakage.
    # Nonetheless, it's often useful for debugging.
    # For access from templates use next tag {% url 'admin:index' %}.
    url(settings.ADMIN_URL, include(admin.site.urls)),
]

if not is_radosure():
    urlpatterns += [
        # Include Zinnia's URLs.

        url(r'', include('blog.urls')),
        # Add Flatpages.
        # WARNING: Be careful with next URLs!
        # The next URLs should be matched with URLs of flatpages.
        url(r'^about_us/$',
            flatpage,
            {'url': '/about_us/'},
            name='fp__about_us'),
        url(r'^radon/how_to_measure/$',
            flatpage,
            {'url': '/radon/how_to_measure/'},
            name='fp__radon__how_to_measure'),
        url(r'^b2b/companies/$',
            flatpage,
            {'url': '/b2b/companies/'},
            name='fp__b2b__companies'),
        url(r'^b2b/housing_associations/$',
            flatpage,
            {'url': '/b2b/housing_associations/'},
            name='fp__b2b__housing_associations'),
        url(r'^b2b/public_municipalities/$',
            flatpage,
            {'url': '/b2b/public_municipalities/'},
            name='fp__b2b__public_municipalities'),
        url(r'^legal/delivery_and_returns/$',
            flatpage,
            {'url': '/legal/delivery_and_returns/'},
            name='fp__legal__delivery_and_returns'),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
        url(r'^restart-supervisor/$',
            RestartSupervisorView.as_view(), name="restart_supervisor"),
    ]


if settings.USE_SILK:
    urlpatterns += [
        url(r'^silk/', include('silk.urls', namespace='silk'))
    ]

if settings.USE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

if settings.DEBUG:
    from django.views.defaults import server_error
    from django.views.defaults import page_not_found
    from django.views.defaults import permission_denied

    urlpatterns += [
        url(r'^500/$', server_error),
        url(r'^403/$', permission_denied, kwargs={'exception': Exception("Permission Denied")}),
        url(r'^404/$', page_not_found, kwargs={'exception': Exception("Page not Found")}),
    ]
