# -*- coding: utf-8 -*-

import os
import sys
from collections import namedtuple
from math import inf

import environ
import raven
from django.utils.translation import ugettext_lazy as _
from oscar import OSCAR_MAIN_TEMPLATE_DIR
from oscar import get_core_apps
from oscar.defaults import *


# CORE CONFIGURATION
# =============================================================================
ROOT_DIR = environ.Path(__file__) - 2  # (/folder/current_file.py - 2 = /)
APPS_DIR = ROOT_DIR.path('radonmeters')

sys.path.append('radonmeters/apps')

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_DEBUG_SQL=(bool, False),
    DJANGO_SECRET_KEY=(str, 'CHANGEME!!!^yyu9d2o)k3mw8@qz1&9er-nmy^4r0d+y@surnowsr&y=33(4w'),
    DJANGO_ADMINS=(list, []),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_STATIC_ROOT=(str, str(APPS_DIR('staticfiles'))),
    DJANGO_MEDIA_ROOT=(str, str(APPS_DIR('media'))),
    DJANGO_DATABASE_URL=(str, 'postgis:///radonmeters'),
    DJANGO_EMAIL_URL=(environ.Env.email_url_config, 'consolemail://'),
    DJANGO_DEFAULT_FROM_EMAIL=(str, 'admin@example.com'),
    DJANGO_EMAIL_BACKEND=(str, 'django.core.mail.backends.smtp.EmailBackend'),
    DJANGO_SERVER_EMAIL=(str, 'root@localhost.com'),

    DJANGO_CELERY_BROKER_URL=(str, 'redis://localhost:6379/0'),
    DJANGO_CELERY_BACKEND=(str, 'redis://localhost:6379/0'),
    DJANGO_CELERY_ALWAYS_EAGER=(bool, False),

    DJANGO_USE_DEBUG_TOOLBAR=(bool, False),
    DJANGO_TEST_RUN=(bool, False),

    DJANGO_HEALTH_CHECK_BODY=(str, 'Success'),
    DJANGO_USE_SILK=(bool, False),

    DEFAULT_SERVICES_GOOGLE_KEY=(str, ''),
    DEFAULT_SERVICES_RETUR_LINK=(str, ''),
    DEFAULT_SERVICES_TRUSTPILOT_TEMPLATE_ID=(str, ''),
    DEFAULT_SERVICES_TRUSTPILOT_BUSINESSUNIT_ID=(str, ''),
    DEFAULT_SERVICES_TRUSTPILOT_LINK=(str, ''),

    DJANGO_MAIN_PERMISSION=(str, ''),
    DEFAULT_LANGUAGE_CODE=(str, 'da')
)

environ.Env.read_env()

DEBUG = env.bool("DJANGO_DEBUG")

SECRET_KEY = env('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

ADMINS = tuple([tuple(admins.split(':')) for admins in env.list('DJANGO_ADMINS')])

MANAGERS = ADMINS

TIME_ZONE = 'UTC'

gettext = lambda s: s

LANGUAGES = (
    ('en', gettext('English')),
    ('da', gettext('Danish')),
    ('sv', gettext('Swedish')),
    ('nn', gettext('Norwegian')),
)

LANGUAGE_CODE = 'en'
DEFAULT_LANGUAGE_CODE = env('DEFAULT_LANGUAGE_CODE')

LOCALE_PATHS = (
    str(ROOT_DIR.path('radonmeters/locale')),
)

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATABASES = {
    'default': env.db('DJANGO_DATABASE_URL')
}

DATE_FORMAT = 'd-m-Y'
DATE_FORMAT_REST = '%d-%m-%Y'
DATE_INPUT_FORMATS = [DATE_FORMAT_REST]
DATETIME_FORMAT = 'd-m-Y, P'
DATETIME_FORMAT_REST = '%d-%m-%Y, %P'
DATETIME_INPUT_FORMATS = [DATETIME_FORMAT_REST, '%d-%m-%Y', "%d-%m-%Y %H:%M"]
SHORT_DATE_FORMAT = 'd-m-Y'
SHORT_DATETIME_FORMAT = 'd-m-Y, P'

FORMAT_MODULE_PATH = [
    'common.formats'
]

DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # For translating data in models:
    'modeltranslation',

    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.postgres',
    'users.apps.UsersConfig',
]

THIRD_PARTY_APPS = [
    'django_extensions',
    'compressor',
    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',

    'constance',
    'constance.backends.database',

    # Needed for Blog:
    'django_comments',
    'mptt',
    'tagging',
    'zinnia',

    # Rest Framework
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    # Translations
    'rosetta',
] + get_core_apps([
    'address',
    'basket',
    'catalogue',
    'checkout',
    'customer',
    'dashboard',
    'dashboard.catalogue',
    'dashboard.communications',
    'dashboard.instructions',
    'dashboard.orders',
    'dashboard.vouchers',
    'dashboard.partners',
    'dashboard.promotions',
    'dashboard.offers',
    'dashboard.owners',
    'dashboard.users',
    'instructions',
    'offer',
    'order',
    'payment',
    'promotions',
    'partner',
])

LOCAL_APPS = [
    'accounting.apps.AccountingConfig',
    'common.apps.CommonConfig',
    'blog.apps.BlogConfig',
    'deliveries.apps.DeliveriesConfig',
    'data_import.apps.DataImportConfig',
    'instructions.apps.InstructionsConfig',

    'providers.stripe_app.apps.StripeConfig',
    'owners.apps.OwnerConfig',

    'url_shortener.apps.UrlShortenerConfig'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# This is needed for keep synchronized history of migrations
# in the database (`django_migrations` table).
MIGRATION_MODULES = {
    'flatpages': 'third_party_apps_migrations.flatpages',
    'zinnia': 'third_party_apps_migrations.zinnia',
}

ADMIN_URL = r'^admin/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'common.middleware.CustomLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',

    # Custom middleware:
    'basket.middleware.BasketMiddleware',
]

# WARNING: Do not change order of backends,
# We use this setting in `ShippingAddressView.form_valid`.
AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_USER_MODEL = 'users.User'


# EMAIL CONFIGURATION
# =============================================================================
EMAIL_URL = env.email_url('DJANGO_EMAIL_URL')
EMAIL_BACKEND = EMAIL_URL['EMAIL_BACKEND']
EMAIL_HOST = EMAIL_URL.get('EMAIL_HOST', '')
if EMAIL_URL.get('EMAIL_HOST_PASSWORD', '') == 'special':
    EMAIL_HOST_PASSWORD = env('DJANGO_EMAIL_HOST_PASSWORD_SPECIAL')
else:
    EMAIL_HOST_PASSWORD = EMAIL_URL.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = EMAIL_URL.get('EMAIL_HOST_USER', '')
EMAIL_PORT = EMAIL_URL.get('EMAIL_PORT', '')
# EMAIL_USE_SSL = 'EMAIL_USE_SSL' in EMAIL_URL
# EMAIL_USE_TLS = 'EMAIL_USE_TLS' in EMAIL_URL
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_FILE_PATH = EMAIL_URL.get('EMAIL_FILE_PATH', '')
EMAIL_SUBJECT_PREFIX = '[RADONMETERS] '

DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL')

CONTACT_US_NOTIFICATION = True


# TEMPLATES CONFIGURATION
# =============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(str(APPS_DIR), 'templates'),
            OSCAR_MAIN_TEMPLATE_DIR
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Django's context processors:
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',

                # Oscar's context processors:
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',

                # Constance's context processors:
                'constance.context_processors.config',

                # Custom's context processors:
                'common.context_processors.additional_data',
            ],
        },
    },
]
TEMPLATE_DEBUG = False


# FILES CONFIGURATION
# =============================================================================
DATA_UPLOAD_MAX_MEMORY_SIZE = None
FILE_UPLOAD_PERMISSIONS = 0o644
THUMBNAIL_PRESERVE_FORMAT = True

STATIC_URL = '/static/'
STATIC_ROOT = env('DJANGO_STATIC_ROOT')

MEDIA_URL = '/media/'
MEDIA_ROOT = env('DJANGO_MEDIA_ROOT')

STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    'compressor.finders.CompressorFinder',
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'


# CELERY CONFIGURATION
# =============================================================================
BROKER_URL = env('DJANGO_CELERY_BROKER_URL')
CELERY_BACKEND = env('DJANGO_CELERY_BACKEND')
CELERY_ALWAYS_EAGER = env.bool('DJANGO_CELERY_ALWAYS_EAGER')
CELERY_TIMEZONE = 'Europe/Copenhagen'


# HAYSTACK CONFIGURATION
# =============================================================================
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}


# OSCAR CONFIGURATION
# =============================================================================
OSCAR_SHOP_NAME = 'Radonmeters'
OSCAR_HOMEPAGE = reverse_lazy('common:home')
OSCAR_FROM_EMAIL = DEFAULT_FROM_EMAIL

# Product classes
OSCAR_PRODUCT_TYPE_DEFAULT = 'Default'
OSCAR_PRODUCT_TYPE_DOSIMETER = 'Dosimeter'

# Currency
# -----------------------------------------------------------------------------
OSCAR_DEFAULT_CURRENCY = 'DKK'
OSCAR_CURRENCY_FORMAT = {
    'DKK': {
        'locale': 'da_DK',
        'format': '#,##0.00 ¤¤',
    },
    None: {
        'locale': 'da_DK',
        'format': '#,##0.00 ¤¤',
    },
}

# Statuses
# -----------------------------------------------------------------------------
OSCAR_INITIAL_ORDER_STATUS = 'created'
OSCAR_INITIAL_LINE_STATUS = 'created'
OSCAR_ORDER_STATUS_PIPELINE = {
    'created': (
        'issued',
        'canceled',
    ),
    'issued': (
        'created',
        'delivery_to_client',
        'canceled',
    ),
    'delivery_to_client': (
        'completed',
        'canceled',
    ),
    'completed': (
        'canceled',
    ),
    'canceled': (),
}

OSCAR_DOSIMETERS_STATUS_PIPELINE = {
    'unknown': ('on_client_side',),
    'on_client_side': ('on_store_side',),
    'on_store_side': ('on_lab_side',),
    'on_lab_side': ('completed',),
    'completed': (),
}

# Offer's conditions
# -----------------------------------------------------------------------------
Condition = namedtuple('Condition', 'low, high, percent')
DOSIMETER_BENEFIT_CONDITIONS = (
    Condition(2, 3, 3),
    Condition(3, 4, 17),
    Condition(4, 5, 18),
    Condition(5, 6, 20),
    Condition(6, 7, 21),
    Condition(7, 8, 23),
    Condition(8, 9, 24),
    Condition(9, 10, 26),
    Condition(10, inf, 27))

# Checkout
# -----------------------------------------------------------------------------
OSCAR_ALLOW_ANON_CHECKOUT = True

# Reviews
# -----------------------------------------------------------------------------
OSCAR_ALLOW_ANON_REVIEWS = False
OSCAR_MODERATE_REVIEWS = True

# Pagination
# -----------------------------------------------------------------------------
# There are a number of settings that control pagination in Oscar’s views.
# They all default to 20.
OSCAR_PRODUCTS_PER_PAGE = 6
OSCAR_OFFERS_PER_PAGE = 20
OSCAR_REVIEWS_PER_PAGE = 20
OSCAR_NOTIFICATIONS_PER_PAGE = 20
OSCAR_EMAILS_PER_PAGE = 20
OSCAR_ORDERS_PER_PAGE = 20
OSCAR_ADDRESSES_PER_PAGE = 20
OSCAR_STOCK_ALERTS_PER_PAGE = 20
OSCAR_DASHBOARD_ITEMS_PER_PAGE = 20

# Navigation
# -----------------------------------------------------------------------------
# Include parts for Fulfillment.
OSCAR_DASHBOARD_NAVIGATION[2]['children'].insert(
    1,
    {
        'label': _('Orders - Dosimeters'),
        'url_name': 'dashboard:dosimeter-list',
    },
)
OSCAR_DASHBOARD_NAVIGATION[2]['children'].insert(
    2,
    {
        'label': _('Orders - Default Products'),
        'url_name': 'dashboard:default-product-list',
    },
)
OSCAR_DASHBOARD_NAVIGATION[2]['children'].append(
    {
        'label': _('Shipments'),
        'url_name': 'dashboard:shipment-list',
    },
)

# Include parts for Offers.
OSCAR_DASHBOARD_NAVIGATION[4]['children'].append(
    {
        'label': _('Send Voucher'),
        'url_name': 'dashboard:send-voucher',
    },
)

# Include parts for Owners.
OSCAR_DASHBOARD_NAVIGATION.append(
    {
        'label': _('Owners'),
        'children': [
            {
                'label': _('Owners'),
                'url_name': 'dashboard:owner-list',
            },
            {
                'label': _('Overview'),
                'url_name': 'dashboard:owner-summary',
            },
            {
                'label': _('Owner report templates'),
                'url_name': 'dashboard:owner-report-template-list',
            },
        ],
    },
)
OSCAR_DASHBOARD_NAVIGATION.append(
    {
        'label': _('Instructions'),
        'children': [
            {
                'label': _('Instruction Templates'),
                'url_name': 'dashboard:instruction-template-list',
            }
        ],
    },
)

OSCAR_DASHBOARD_DEFAULT_ACCESS_FUNCTION = 'config.permission.custom_access_fn'

# PAYMENT SYSTEMS: STRIPE
# =============================================================================
STRIPE_SK = env('STRIPE_SK', default='')
STRIPE_PK = env('STRIPE_PK', default='')


# VATs:
# =============================================================================
VAT_PERCENT_DA = 0.25


# DELIVERIES
# =============================================================================
DELIVERY_AUTH_LOGIN = env('DELIVERY_AUTH_LOGIN', default='')
DELIVERY_AUTH_PASSWORD = env('DELIVERY_AUTH_PASSWORD', default='')
DELIVERY_BASE_URL = env('DELIVERY_BASE_URL', default='')
DELIVERY_TEST_MODE = env.bool('DELIVERY_TEST_MODE', default=True)

DELIVERY_OUT_OWN_AGREEMENT = True
DELIVERY_OUT_LABEL_FORMAT = None
DELIVERY_OUT_PRODUCT_CODE = 'PDK_MC'
DELIVERY_OUT_SERVICE_CODES = "EMAIL_NT,SMS_NT"
DELIVERY_OUT_AUTOMATIC_SELECT_SERVICE_POINT = True

DELIVERY_BACK_OWN_AGREEMENT = True
DELIVERY_BACK_LABEL_FORMAT = None
DELIVERY_BACK_PRODUCT_CODE = "PDK_RDO"
DELIVERY_BACK_SERVICE_CODES = "EMAIL_NT",
DELIVERY_BACK_AUTOMATIC_SELECT_SERVICE_POINT = True

# CRYPTOGRAPHY
# =============================================================================
FERNET_KEY = env('FERNET_KEY')


# BLOG (ZINNIA)
# =============================================================================
ZINNIA_ENTRY_BASE_MODEL = 'blog.models.Entry'
ZINNIA_PAGINATION = 10


# CKEDITOR
# =============================================================================
CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Full',
        'height': 291,
        'width': 835,
        'filebrowserWindowWidth': 940,
        'filebrowserWindowHeight': 725,
        'toolbar_Full2': [
            ['Source'],
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-',
             'Undo', 'Redo', '-'],
            '/',
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-',
             'CopyFormatting', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-',
             'Outdent', 'Indent', '-',
             'Blockquote', 'CreateDiv', '-',
             'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-',
             'BidiLtr', 'BidiRtl', 'Language'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak'],
            '/',
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks'],
            ['-'],
            ['About']
        ]
    }
}


# CONSTANCE
# =============================================================================
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_ADDITIONAL_FIELDS = {
    'image_field': ['django.forms.ImageField', {}]
}
CONSTANCE_CONFIG = {
    'SOCIAL_LINK_FACEBOOK': ('', '', str),
    'SOCIAL_LINK_TWITTER': ('', '', str),
    'SOCIAL_LINK_YOUTUBE': ('', '', str),
    'SOCIAL_ACCOUNT_TWITTER': ('@radonmeters', '', str),

    'CONTACT_INFO_ADDRESS': ('', '', str),
    'CONTACT_INFO_EMAIL': ('', '', str),
    'CONTACT_INFO_PHONE_NUMBER': ('', '', str),
    'CONTACT_INFO_CVR_NUMBER': ('', '', str),
    'CONTACT_INFO_BANK_NAME': ('', '', str),
    'CONTACT_INFO_REGISTRATION_NUMBER': ('', '', str),
    'CONTACT_INFO_ACCOUNT_NUMBER': ('', '', str),

    'BUSINESS_NAME': ('BUSINESS NAME', '', str),
    'BUSINESS_PHONE_NUMBER': ('BUSINESS PHONE NUMBER', '', str),
    'BUSINESS_EMAIL': ('BUSINESS EMAIL', '', str),
    'BUSINESS_ADDRESS_LINE': ('BUSINESS ADDRESS LINE', '', str),
    'BUSINESS_ADDRESS_CITY': ('BUSINESS ADDRESS CITY', '', str),
    'BUSINESS_ADDRESS_STATE': ('BUSINESS ADDRESS STATE', '', str),
    'BUSINESS_ADDRESS_POST_CODE': ('BUSINESS ADDRESS POST CODE', '', str),

    'DELIVERY_NAME': ('Healthyhouse Radonmeters ApS', '', str),
    'DELIVERY_ADDRESS1': ('Frederiksberggade 2, 5. sal', '', str),
    'DELIVERY_ADDRESS2': ('', '', str),
    'DELIVERY_COUNTRY_CODE': ('DK', '', str),
    'DELIVERY_ZIPCODE': ('1459', '', str),
    'DELIVERY_CITY': ('København K', '', str),
    'DELIVERY_ATTENTION': ('', '', str),
    'DELIVERY_EMAIL': ('package@radonmeters.com', '', str),
    'DELIVERY_TELEPHONE': ('23362260', '', str),
    'DELIVERY_MOBILE': ('23362260', '', str),
    'DELIVERY_INSTRUCTION': ('', '', str),
    'DELIVERY_PARCEL_NUMBER': (1, '', int),

    'DOSIMETERS_MANUAL_NOTIFICATIONS': (True, '', bool),
    'DOSIMETERS_REPORT_LOGO': ('', '', 'image_field'),
    'DOSIMETERS_REPORT_LANGUAGE': (
        'da', 'Default language for report. One of [en, da, sv, nn]', str),

    'SERVICES_GOOGLE_KEY': ('', '', str),
    'SERVICES_GOOGLE_TAG_MANAGER': ('', '', str),
    'SERVICES_GOOGLE_SEARCH_CONSOLE': ('', '', str),
    'SERVICES_GOOGLE_ANALYTICS': ('', '', str),
    'SERVICES_GOOGLE_RECAPTCHA_KEY': ('', '', str),
    'SERVICES_GOOGLE_RECAPTCHA_SECRET_KEY': ('', '', str),
    'SERVICES_ZENDESK_SCRIPT': (
        '',
        'You have to remove <script> tags. \n'
        'So you should add variable beginning from window.zEmbed',
        str),
    'SERVICES_RETUR_LINK': ('', '', str),
    'SERVICES_TRUSTPILOT_TEMPLATE_ID': ('', '', str),
    'SERVICES_TRUSTPILOT_LINK': ('', '', str),
    'SERVICES_TRUSTPILOT_BUSINESSUNIT_ID': ('', '', str),
}
CONSTANCE_CONFIG_FIELDSETS = {
    'Options': CONSTANCE_CONFIG.keys(),
}

SERVICES_GOOGLE_RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

# ROSETTA
# =============================================================================
ROSETTA_SHOW_AT_ADMIN_PANEL = True
ROSETTA_MESSAGES_PER_PAGE = 100


# REST FRAMEWORK
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'SEARCH_PARAM': 'q',
    'DATE_FORMAT': DATE_FORMAT_REST,
    'DATE_INPUT_FORMATS': [DATE_FORMAT_REST],
    'DATETIME_FORMAT': DATETIME_FORMAT_REST,
    'DATETIME_INPUT_FORMATS': DATETIME_INPUT_FORMATS
}


# LOGGING CONFIGURATION
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'dashboard': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    }
}

if env.bool('DJANGO_DEBUG_SQL'):
    LOGGING['loggers']['django.db.backends'] = {
        'handlers': ['console'],
        'propagate': False,
        'level': 'DEBUG',
    }


if os.environ.get('SENTRY_DSN'):
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)
    RAVEN_CONFIG = {
        'dsn': env('SENTRY_DSN'),
        'release': raven.fetch_git_sha(str(ROOT_DIR)),
    }


if env.bool('DJANGO_TEST_RUN'):
    pass


USE_DEBUG_TOOLBAR = env.bool('DJANGO_USE_DEBUG_TOOLBAR')
if USE_DEBUG_TOOLBAR:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'DISABLE_PANELS': [
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ],
        'SHOW_TEMPLATE_CONTEXT': True,
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

    # http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
    INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', '10.0.2.2')


USE_SILK = env('DJANGO_USE_SILK')
if USE_SILK:
    INSTALLED_APPS += (
        'silk',
    )
    MIDDLEWARE += [
        'silk.middleware.SilkyMiddleware',
    ]
    SILKY_AUTHENTICATION = True  # User must login
    SILKY_AUTHORISATION = True  # User must have permissions
    SILKY_PERMISSIONS = lambda user: user.is_superuser


HEALTH_CHECK_BODY = env('DJANGO_HEALTH_CHECK_BODY')

# SSL AND SECURITY
# =============================================================================
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r'^checker/$', ]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DEFAULT_SERVICES = {
    'GOOGLE_KEY': env.str('DEFAULT_SERVICES_GOOGLE_KEY'),
    'RETUR_LINK':  env.str('DEFAULT_SERVICES_RETUR_LINK'),
    'TRUSTPILOT_TEMPLATE_ID': env.str('DEFAULT_SERVICES_TRUSTPILOT_TEMPLATE_ID'),
    'TRUSTPILOT_BUSINESSUNIT_ID':  env.str('DEFAULT_SERVICES_TRUSTPILOT_BUSINESSUNIT_ID'),
    'TRUSTPILOT_LINK': env.str('DEFAULT_SERVICES_TRUSTPILOT_LINK'),
}

RADOSURE_NAME = 'radosure'
MAIN_PERMISSION = env.str('DJANGO_MAIN_PERMISSION')
