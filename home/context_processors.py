from pathlib import Path

from django.conf import settings
from django.core.cache import cache

from home.models import AboutMe, Blog

USED_TAGS_CACHE_KEY = "used_tags"
USED_TAGS_CACHE_TTL = 300  # 5 minutes
STATIC_ASSET_VERSION_CACHE_KEY = "static_asset_version"
STATIC_ASSET_VERSION_CACHE_TTL = 300  # 5 minutes

# Sentinel: distinguishes "key not in cache" from "key in cache with value None".
# cache.get() returns None for both cases, so we use this sentinel as the default.
_CACHE_MISS = object()


def used_tags(request):
    """Provide a list of distinct categories (used as tags) to templates."""
    tags = cache.get(USED_TAGS_CACHE_KEY)
    if tags is None:
        tags = list(
            Blog.objects.exclude(category__isnull=True)
            .exclude(category__exact="")
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )
        cache.set(USED_TAGS_CACHE_KEY, tags, USED_TAGS_CACHE_TTL)
    return {"used_tags": tags}


def static_asset_version(request):
    """Expose a cache-busting version string for static assets.

    In production, WhiteNoise's CompressedManifestStaticFilesStorage already
    fingerprints file names, so we simply reuse the settings-provided value.
    In development, we derive the version from the latest static file mtime so
    the browser always picks up freshly edited CSS/JS without a hard refresh.
    """
    cached = cache.get(STATIC_ASSET_VERSION_CACHE_KEY)
    if cached:
        return {"STATIC_ASSET_VERSION": cached}

    if not settings.DEBUG:
        # Production: WhiteNoise handles cache-busting via hashed filenames.
        # Use the build-time version from settings — no filesystem scan needed.
        version = getattr(settings, "STATIC_ASSET_VERSION", "1")
        # Cache indefinitely; cleared only on server restart (which implies a deploy).
        cache.set(STATIC_ASSET_VERSION_CACHE_KEY, version, None)
        return {"STATIC_ASSET_VERSION": version}

    # Development: scan static files for the latest mtime to auto-bust cache.
    static_dir = Path(settings.BASE_DIR) / "static"
    latest_mtime = 0
    if static_dir.exists():
        for asset_path in static_dir.rglob("*"):
            if asset_path.is_file() and asset_path.suffix.lower() in {
                ".css",
                ".js",
                ".map",
            }:
                latest_mtime = max(latest_mtime, int(asset_path.stat().st_mtime_ns))

    version = str(latest_mtime or getattr(settings, "STATIC_ASSET_VERSION", "1"))
    cache.set(STATIC_ASSET_VERSION_CACHE_KEY, version, STATIC_ASSET_VERSION_CACHE_TTL)
    return {"STATIC_ASSET_VERSION": version}


def about_me(request):
    """Provide the AboutMe singleton to all templates for footer/social links."""
    about_me_obj = cache.get("about_me_singleton", _CACHE_MISS)
    if about_me_obj is _CACHE_MISS:
        about_me_obj = AboutMe.objects.first()
        cache.set(
            "about_me_singleton", about_me_obj, 86400 * 30
        )  # 30 days, cleared by signal
    return {"about_me": about_me_obj}
