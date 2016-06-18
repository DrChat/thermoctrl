from django.conf import settings
from django.http import HttpResponseRedirect

SSL = 'SSL'

def request_is_secure(request):
    if request.is_secure():
        return True

    # Handle forwarded SSL (used at Webfaction)
    if 'HTTP_X_FORWARDED_SSL' in request.META:
        return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

    if 'HTTP_X_SSL_REQUEST' in request.META:
        return request.META['HTTP_X_SSL_REQUEST'] == '1'

    return False

def get_secure_url(request, secure):
    proto = secure and "https" or "http"

    return "%s://%s%s" % (proto, request.get_host(), request.get_full_path())

class SSLRedirect:
    def process_request(self, request):
        if request_is_secure(request):
            request.IS_SECURE=True
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):          
        if SSL in view_kwargs:
            secure = view_kwargs[SSL]
            del view_kwargs[SSL]
        else:
            secure = False

        if settings.DEBUG:
            return None

        if getattr(settings, "TESTMODE", False):
            return None

        # Don't downgrade the user if we're already secure
        if not secure:
            return None

        if not secure == request_is_secure(request):
            return self._redirect(request, secure)

    def _redirect(self, request, secure):
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError(
            """Django can't perform a SSL redirect while maintaining POST data.
                Please structure your views so that redirects only occur during GETs.""")

        return HttpResponseRedirect(get_secure_url(request, secure))