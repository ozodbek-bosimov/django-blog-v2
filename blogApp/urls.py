from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from home.sitemaps import BlogPostSitemap, CategorySitemap, StaticViewSitemap

# from django.urls import re_path as url
# from django.conf import settings
# from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': {
            'static': StaticViewSitemap,
            'posts': BlogPostSitemap,
            'categories': CategorySitemap,
        }},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('', include('home.urls')),
    # url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
