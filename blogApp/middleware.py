from datetime import timedelta

from django.contrib.admin.models import LogEntry
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


class AdminSessionTimeoutMiddleware:
    CLEANUP_LAST_RUN_CACHE_KEY = "admin_log_cleanup:last_run_ts"
    CLEANUP_LOCK_CACHE_KEY = "admin_log_cleanup:lock"
    CLEANUP_INTERVAL_SECONDS = 24 * 60 * 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/") and request.user.is_authenticated:
            request.session.set_expiry(settings.ADMIN_SESSION_TIMEOUT)
            self._cleanup_admin_log_if_needed()
        return self.get_response(request)

    def _cleanup_admin_log_if_needed(self):
        if not getattr(settings, "ADMIN_LOG_RETENTION_ENABLED", True):
            return

        retention_days = max(int(getattr(settings, "ADMIN_LOG_RETENTION_DAYS", 90)), 1)
        now_ts = timezone.now().timestamp()
        last_run_ts = cache.get(self.CLEANUP_LAST_RUN_CACHE_KEY)
        if last_run_ts and now_ts - float(last_run_ts) < self.CLEANUP_INTERVAL_SECONDS:
            return

        # Use a short lock to avoid duplicate cleanup across concurrent requests.
        if not cache.add(self.CLEANUP_LOCK_CACHE_KEY, "1", timeout=60):
            return

        try:
            cutoff = timezone.now() - timedelta(days=retention_days)
            LogEntry.objects.filter(action_time__lt=cutoff).delete()
            cache.set(
                self.CLEANUP_LAST_RUN_CACHE_KEY,
                now_ts,
                timeout=self.CLEANUP_INTERVAL_SECONDS,
            )
        finally:
            cache.delete(self.CLEANUP_LOCK_CACHE_KEY)
