from home.models import Blog

def used_tags(request):
    """Provide a list of distinct categories (used as tags) to templates."""
    tags = list(Blog.objects.values_list('category', flat=True).distinct().order_by('category'))
    return {'used_tags': tags}
