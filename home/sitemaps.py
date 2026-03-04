from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from home.models import Blog


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'blog', 'projects', 'categories']

    def location(self, item: str) -> str:
        return reverse(item)


class BlogPostSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Blog.objects.all().order_by('-time')

    def lastmod(self, obj: Blog):
        return obj.time

    def location(self, obj: Blog) -> str:
        return reverse('blogpost', args=[obj.slug])


class CategorySitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return (
            Blog.objects.exclude(category__isnull=True)
            .exclude(category__exact='')
            .values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )

    def location(self, item: str) -> str:
        return reverse('category', args=[item])
