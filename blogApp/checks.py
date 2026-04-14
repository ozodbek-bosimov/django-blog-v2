"""Django system checks for deployment configuration."""

from django.core.checks import Warning, register


@register(deploy=True)
def warn_locmem_cache_in_production(app_configs, **kwargs):
    """
    LocMemCache is per-process. Multiple Gunicorn/Uvicorn workers do not share it,
    so model-driven cache invalidation only affects the worker that handled the save.
    """
    from django.conf import settings

    if settings.DEBUG:
        return []

    backend = settings.CACHES.get("default", {}).get("BACKEND", "")
    if "LocMemCache" in backend:
        return [
            Warning(
                "Default cache uses LocMemCache. With multiple workers, cache "
                "invalidation is not shared across processes, so visitors may see stale "
                "lists and blog pages until keys expire. Set DJANGO_REDIS_URL for a "
                "shared Redis cache.",
                id="blogapp.W001",
            )
        ]
    return []
