from django.core.cache import cache

from home.models import Blog

USED_TAGS_CACHE_KEY = 'used_tags'
USED_TAGS_CACHE_TTL = 300  # 5 minutes


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
