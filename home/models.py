import re
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Blog(models.Model):
    sno = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    meta = models.CharField(max_length=300)
    content = models.TextField()
    thumbnail_img = models.ImageField(null=True, blank=True, upload_to="images/")
    thumbnail_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=255, default="uncategorized")
    slug = models.CharField(max_length=100)
    time = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def effective_thumbnail(self):
        """Return the URL to use for the thumbnail, preferring the uploaded image."""
        if self.thumbnail_img and hasattr(self.thumbnail_img, 'url'):
            return self.thumbnail_img.url
        return self.thumbnail_url or ''


class AboutMe(models.Model):
    """Singleton model for About Me section"""
    name = models.CharField(max_length=100)
    profession = models.CharField(max_length=150)
    bio = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    profile_image_url = models.URLField(help_text="CDN URL for profile image")
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True, help_text="X (formerly Twitter) profile URL")
    leetcode_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Enforce singleton pattern - only one AboutMe instance allowed"""
        if not self.pk and AboutMe.objects.exists():
            # Delete all existing instances
            AboutMe.objects.all().delete()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "About Me"
        verbose_name_plural = "About Me"


class Skill(models.Model):
    """Skills with percentage proficiency"""
    name = models.CharField(max_length=100)
    percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Skill proficiency (0-100)"
    )
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")

    def __str__(self):
        return f"{self.name} - {self.percentage}%"

    class Meta:
        ordering = ['order', 'name']


class Project(models.Model):
    """Portfolio projects"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail_url = models.URLField(help_text="CDN URL for project thumbnail")
    github_link = models.URLField(blank=True)
    demo_link = models.URLField(blank=True)
    technologies = models.CharField(max_length=500, help_text="Comma-separated technologies")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_technologies_list(self):
        """Return technologies as a list"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
        return []

    class Meta:
        ordering = ['order', '-created_at']


# signals for cleaning up image files when a Blog is changed or removed
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


def _extract_media_paths_from_html(html_content):
    if not html_content:
        return set()

    media_url = settings.MEDIA_URL or '/media/'
    if not media_url.endswith('/'):
        media_url = f"{media_url}/"

    paths = set()
    for raw_url in re.findall(r'(?:src|href)=["\']([^"\']+)["\']', html_content):
        parsed_path = urlparse(raw_url).path
        if parsed_path.startswith(media_url):
            relative_path = parsed_path[len(media_url):].lstrip('/')
            if relative_path:
                paths.add(relative_path)
    return paths


def _is_media_still_referenced(relative_path, exclude_aboutme_pk=None, exclude_blog_pk=None):
    media_url = settings.MEDIA_URL or '/media/'
    if not media_url.endswith('/'):
        media_url = f"{media_url}/"
    absolute_media_url = f"{media_url}{relative_path}"

    aboutme_qs = AboutMe.objects.all()
    if exclude_aboutme_pk:
        aboutme_qs = aboutme_qs.exclude(pk=exclude_aboutme_pk)

    blog_qs = Blog.objects.all()
    if exclude_blog_pk:
        blog_qs = blog_qs.exclude(pk=exclude_blog_pk)

    return (
        aboutme_qs.filter(bio__icontains=absolute_media_url).exists()
        or blog_qs.filter(content__icontains=absolute_media_url).exists()
    )


def _delete_media_paths_if_unused(media_paths, exclude_aboutme_pk=None, exclude_blog_pk=None):
    for path in media_paths:
        if _is_media_still_referenced(
            path,
            exclude_aboutme_pk=exclude_aboutme_pk,
            exclude_blog_pk=exclude_blog_pk,
        ):
            continue
        if default_storage.exists(path):
            default_storage.delete(path)


@receiver(post_delete, sender=Blog)
def delete_thumbnail_on_delete(sender, instance, **kwargs):
    """Remove file from filesystem when Blog object is deleted."""
    if instance.thumbnail_img:
        instance.thumbnail_img.delete(save=False)


@receiver(pre_save, sender=Blog)
def delete_old_thumbnail_on_change(sender, instance, **kwargs):
    """Delete old file when replacing thumbnail_img with a new one."""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if old.thumbnail_img and old.thumbnail_img != instance.thumbnail_img:
        old.thumbnail_img.delete(save=False)


@receiver(pre_save, sender=Blog)
def delete_removed_blog_content_media(sender, instance, **kwargs):
    """Delete media files removed from Blog.content when they are no longer used."""
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_media = _extract_media_paths_from_html(old_instance.content)
    new_media = _extract_media_paths_from_html(instance.content)
    removed_media = old_media - new_media

    _delete_media_paths_if_unused(removed_media, exclude_blog_pk=instance.pk)


@receiver(post_delete, sender=Blog)
def delete_blog_content_media_on_delete(sender, instance, **kwargs):
    """Delete media files from Blog.content on object delete when no longer used."""
    removed_media = _extract_media_paths_from_html(instance.content)
    _delete_media_paths_if_unused(removed_media)


@receiver(pre_save, sender=AboutMe)
def delete_removed_aboutme_bio_media(sender, instance, **kwargs):
    """Delete media files removed from AboutMe.bio when they are no longer used."""
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_media = _extract_media_paths_from_html(old_instance.bio)
    new_media = _extract_media_paths_from_html(instance.bio)
    removed_media = old_media - new_media

    _delete_media_paths_if_unused(removed_media, exclude_aboutme_pk=instance.pk)


@receiver(post_delete, sender=AboutMe)
def delete_aboutme_bio_media_on_delete(sender, instance, **kwargs):
    """Delete media files from AboutMe.bio on object delete when no longer used."""
    removed_media = _extract_media_paths_from_html(instance.bio)
    _delete_media_paths_if_unused(removed_media)
