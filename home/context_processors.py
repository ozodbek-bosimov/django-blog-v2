from pathlib import Path

from django.core.cache import cache
from django.conf import settings

from home.models import Blog

USED_TAGS_CACHE_KEY = 'used_tags'
USED_TAGS_CACHE_TTL = 300  # 5 minutes
STATIC_ASSET_VERSION_CACHE_KEY = 'static_asset_version'
STATIC_ASSET_VERSION_CACHE_TTL = 300  # 5 minutes


def used_tags(request):
    """Provide a list of distinct categories (used as tags) to templates."""
    tags = cache.get(USED_TAGS_CACHE_KEY)
    if tags is None:
        tags = list(
            Blog.objects
            .exclude(category__isnull=True)
            .exclude(category__exact='')
            .values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )
        cache.set(USED_TAGS_CACHE_KEY, tags, USED_TAGS_CACHE_TTL)
    return {'used_tags': tags}


def static_asset_version(request):
    """Expose a cache-busting version derived from local static file mtimes."""
    cached = cache.get(STATIC_ASSET_VERSION_CACHE_KEY)
    if cached:
        return {'STATIC_ASSET_VERSION': cached}

    static_dir = Path(settings.BASE_DIR) / 'static'
    latest_mtime = 0
    if static_dir.exists():
        for asset_path in static_dir.rglob('*'):
            if asset_path.is_file() and asset_path.suffix.lower() in {'.css', '.js', '.map'}:
                latest_mtime = max(latest_mtime, int(asset_path.stat().st_mtime_ns))

    version = str(latest_mtime or getattr(settings, 'STATIC_ASSET_VERSION', '1'))
    cache.set(STATIC_ASSET_VERSION_CACHE_KEY, version, STATIC_ASSET_VERSION_CACHE_TTL)
    return {'STATIC_ASSET_VERSION': version}
