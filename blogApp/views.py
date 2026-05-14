from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def admin_keepalive(request):
    """Refresh admin session expiry. Called periodically by JavaScript.

    Returns 200 if the session is alive, 401 if expired.
    We intentionally avoid @staff_member_required because its redirect
    makes fetch() follow to the login page (200 HTML) and the JS
    can't distinguish a live session from an expired one.
    """
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({"status": "expired"}, status=401)
    return JsonResponse({"status": "ok"})
