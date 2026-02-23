from django.contrib.sitemaps import Sitemap
from django.db.models import Model
from django.urls import reverse
from typing import cast

from home.models import Blog


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'blog', 'projects', 'categories']

    def location(self, obj: Model) -> str:
        return reverse(cast(str, obj))


class BlogPostSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Blog.objects.all().order_by('-time')

    def lastmod(self, obj: Model):
        return cast(Blog, obj).time

    def location(self, obj: Model) -> str:
        blog = cast(Blog, obj)
        return reverse('blogpost', args=[blog.slug])


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

    def location(self, obj: Model) -> str:
        return reverse('category', args=[cast(str, obj)])
