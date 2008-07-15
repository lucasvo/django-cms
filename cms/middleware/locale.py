"this is the locale selecting middleware that will look at accept headers"

from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.utils.translation import check_for_language
from django.http import HttpResponseRedirect
from django.conf import settings
from django.middleware.locale import LocaleMiddleware

class LocaleMiddleware(LocaleMiddleware):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context. This allows pages to be dynamically
    translated to the language the user desires (if the language
    is available, of course).
    This is a modified version of django's base LocaleMiddleware.
    It integrates the set_language() django i18n view and allows
    to change language state over GET in addition to the introduced
    restriction to only allow POST language state change (see
    http://code.djangoproject.com/wiki/BackwardsIncompatibleChanges#django.views.i18n.set_languagerequiresaPOSTrequest
    for more information). Use "language" as GET parameter (?language=xx).
    """

    def process_request(self, request):
        language = translation.get_language_from_request(request)
        requested_language = request.REQUEST.get('language', None)
        if requested_language and requested_language != language \
        and check_for_language(requested_language):
            language = requested_language
            if hasattr(request, 'session'):
                request.session['django_language'] = language
            else:
                next = request.REQUEST.get('next', None)
                if not next:
                    next = request.META.get('HTTP_REFERER', None)
                if not next:
                    next = '/'
                response = HttpResponseRedirect(next)
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
                return response
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
