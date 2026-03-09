from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse


@staff_member_required
def admin_keepalive(request):
    """Refresh admin session expiry. Called periodically by JavaScript."""
    return JsonResponse({"status": "ok"})
