from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from home.sitemaps import BlogPostSitemap, CategorySitemap, StaticViewSitemap
from blogApp.views import admin_keepalive


urlpatterns = [
    path('_owner/keepalive/', admin_keepalive, name='admin_keepalive'),
    path('_owner/', admin.site.urls),
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
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'
    ), name='robots'),
    path('404/', TemplateView.as_view(template_name='404.html'), name='test_404'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'home.views.custom_404'
