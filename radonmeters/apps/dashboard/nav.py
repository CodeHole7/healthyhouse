import logging
import warnings
from functools import lru_cache

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, resolve, reverse

from oscar.views.decorators import check_permissions

logger = logging.getLogger('oscar.dashboard')


def custom_access_fn(user, url_name, url_args=None, url_kwargs=None):

    return False
    """
    Given a user and a url_name, this function assesses whether the
    user has the right to access the URL.
    Once the permissions for the view are known, the access logic used
    by the dashboard decorator is evaluated
    """
    if url_name is None:  # it's a heading
        return True

    try:
        url = reverse(url_name, args=url_args, kwargs=url_kwargs)
    except NoReverseMatch:
        logger.exception('Invalid URL name {}'.format(url_name))
        warnings.warn(
            'Invalid URL names supplied to oscar.dashboard.nav.default_access_fn'
            'will throw an exception in Oscar 2.1',
            RemovedInOscar21Warning,
            stacklevel=2
        )
        return False

    url_match = resolve(url)
    url_name = url_match.url_name
    try:
        app_config_instance = _dashboard_url_names_to_config()[url_name]
    except KeyError:
        logger.error(
            "{} is not a valid dashboard URL".format(url_match.view_name)
        )
        warnings.warn(
            'Invalid URL names supplied to oscar.dashboard.nav.default_access_fn'
            'will throw an exception in Oscar 2.1',
            RemovedInOscar21Warning,
            stacklevel=2
        )
        return False

    permissions = app_config_instance.get_permissions(url_name)

    return check_permissions(user, permissions)