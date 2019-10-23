from celery.utils.log import get_task_logger
from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.utils import translation

from common.utils import get_allowed_language_code

logger = get_task_logger(__name__)


class CustomLocaleMiddleware(LocaleMiddleware):
    """
    CustomLocaleMiddleware, does auto detection which language
    need to activate for current user session, according to logic below
    """
    DEFAULT_LANGUAGE_CODE = settings.DEFAULT_LANGUAGE_CODE

    def process_request(self, request):
        # Set default language by code from
        # HEADERS DATA or LANGUAGE SESSION KEY ('en' for e.g.)
        language = self.get_language_code(request=request)

        # Activate selected language.
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def get_language_code(self, request):
        """
        Get current user language code.
        Logic based on http headers or session data.

        :param request:
        :return: language_code in format ('en' for e.g.) or None
        """
        # When user has LANGUAGE_SESSION_KEY use it.
        language_session_key = request.session.get(translation.LANGUAGE_SESSION_KEY)
        
        if language_session_key:
            return language_session_key

        # we always return the Danish language.
        return self.DEFAULT_LANGUAGE_CODE

        # When user hasn't LANGUAGE_SESSION_KEY,
        # take lang_code from HTTP HEADERS.
        language_full_name = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language_full_name:
            language_code = get_allowed_language_code(language_full_name[:2])
            if language_code:
                # Remember language code with session
                if hasattr(request, 'session'):
                    request.session[translation.LANGUAGE_SESSION_KEY] = language_code
                return language_code
            else:
                return self.DEFAULT_LANGUAGE_CODE
