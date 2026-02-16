from django.conf import settings


class AdminSessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/") and request.user.is_authenticated:
            request.session.set_expiry(settings.ADMIN_SESSION_TIMEOUT)
        return self.get_response(request)
