from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from blogApp.views import admin_keepalive
from home.sitemaps import BlogPostSitemap, StaticViewSitemap, TopicSitemap

urlpatterns = [
    path("_owner/keepalive/", admin_keepalive, name="admin_keepalive"),
    path("_owner/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "static": StaticViewSitemap,
                "posts": BlogPostSitemap,
                "topics": TopicSitemap,
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", include("home.urls")),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.SHARED_URL, document_root=settings.SHARED_ROOT)

handler404 = "home.views.custom_404"
