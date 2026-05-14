import re
from io import BytesIO
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from PIL import Image


def _compress_and_rename_image(image_field, max_size=(1000, 1000), quality=80):
    """Compresses an image field using Pillow to save disk space and bandwidth.

    Converts images to WebP format for superior compression.  Transparent
    images (RGBA / P with transparency) are kept as WebP with alpha;
    everything else is converted to RGB first.
    """
    if not image_field:
        return image_field

    # Only process *new* uploads (not already-saved files)
    if getattr(image_field, "_committed", True):
        return image_field

    try:
        # Reset file pointer — critical for files that have been partially
        # read during Django's upload validation / CKEditor processing.
        if hasattr(image_field, "seek"):
            image_field.seek(0)

        img = Image.open(image_field)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Decide whether to keep alpha channel
        has_alpha = img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        )
        if not has_alpha:
            img = img.convert("RGB")

        output = BytesIO()
        img.save(output, format="WEBP", quality=quality, method=4)
        compressed_size = output.tell()
        output.seek(0)

        original_name = getattr(image_field, "name", "img") or "img"
        base_name = original_name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        new_name = f"{base_name}.webp"

        return InMemoryUploadedFile(
            output, "ImageField", new_name, "image/webp", compressed_size, None
        )
    except Exception:
        # Reset pointer so Django can still save the original file
        if hasattr(image_field, "seek"):
            image_field.seek(0)
        return image_field


# Create your models here.
class Blog(models.Model):
    sno = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    meta = models.CharField(max_length=600)
    content = models.TextField()
    thumbnail_img = models.ImageField(null=True, blank=True, upload_to="images/")
    thumbnail_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=255, default="uncategorized")
    slug = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.category:
            self.category = self.category.strip().lower()

        if self.thumbnail_img:
            self.thumbnail_img = _compress_and_rename_image(
                self.thumbnail_img, max_size=(1280, 720), quality=90
            )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    @property
    def effective_thumbnail(self):
        """Return the URL to use for the thumbnail, preferring the uploaded image."""
        if self.thumbnail_img and hasattr(self.thumbnail_img, "url"):
            return self.thumbnail_img.url
        return self.thumbnail_url or ""

    def get_absolute_thumbnail_url(self, request):
        """Return the absolute URL for the thumbnail, including scheme and host."""
        img_url = self.effective_thumbnail
        if img_url and not img_url.startswith(("http://", "https://")):
            return f"{request.scheme}://{request.get_host()}{img_url}"
        return img_url


class AboutMe(models.Model):
    """Singleton model for About Me section"""

    name = models.CharField(max_length=100)
    profession = models.CharField(max_length=150)
    bio = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    profile_img = models.ImageField(null=True, blank=True, upload_to="profile/")
    profile_image_url = models.URLField(
        blank=True, help_text="CDN URL for profile image (used if no image is uploaded)"
    )
    hero_img = models.ImageField(null=True, blank=True, upload_to="hero/")
    hero_image_url = models.URLField(
        blank=True, help_text="CDN URL for the homepage hero background image"
    )
    resume_file = models.FileField(
        null=True,
        blank=True,
        upload_to="resume/",
        help_text="Upload your resume file directly (e.g. PDF)",
    )
    resume_url = models.URLField(
        blank=True,
        help_text="External URL for your resume (used if no file is uploaded)",
    )
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True, help_text="X (formerly Twitter) profile URL")
    leetcode_url = models.URLField(blank=True)

    @property
    def effective_resume(self):
        """Return the uploaded resume file URL if it exists, otherwise the external resume URL."""
        if self.resume_file and hasattr(self.resume_file, "url"):
            return self.resume_file.url
        return self.resume_url or ""

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Enforce singleton pattern - only one AboutMe instance allowed"""
        if not self.pk and AboutMe.objects.exists():
            # Update the existing instance instead of deleting
            existing = AboutMe.objects.first()
            self.pk = existing.pk

        if self.profile_img:
            self.profile_img = _compress_and_rename_image(
                self.profile_img, max_size=(800, 800), quality=95
            )
        if self.hero_img:
            self.hero_img = _compress_and_rename_image(
                self.hero_img, max_size=(2560, 1440), quality=85
            )

        super().save(*args, **kwargs)

    @property
    def effective_profile_image(self):
        """Return the URL to use for the profile image, preferring the uploaded image."""
        if self.profile_img and hasattr(self.profile_img, "url"):
            return self.profile_img.url
        return self.profile_image_url or ""

    @property
    def effective_hero_image(self):
        """Return the URL to use for the hero background image."""
        if self.hero_img and hasattr(self.hero_img, "url"):
            return self.hero_img.url
        return self.hero_image_url or ""

    def get_absolute_profile_image_url(self, request):
        """Return the absolute URL for the profile image, including scheme and host."""
        img_url = self.effective_profile_image
        if img_url and not img_url.startswith(("http://", "https://")):
            return f"{request.scheme}://{request.get_host()}{img_url}"
        return img_url

    def get_absolute_hero_image_url(self, request):
        """Return the absolute URL for the hero image, including scheme and host."""
        img_url = self.effective_hero_image
        if img_url and not img_url.startswith(("http://", "https://")):
            return f"{request.scheme}://{request.get_host()}{img_url}"
        return img_url

    class Meta:
        verbose_name = "About Me"
        verbose_name_plural = "About Me"


class Skill(models.Model):
    """Skills with percentage proficiency"""

    name = models.CharField(max_length=100)
    percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Skill proficiency (0-100)",
    )
    order = models.IntegerField(
        default=0, help_text="Display order (lower numbers first)"
    )

    def __str__(self):
        return f"{self.name} - {self.percentage}%"

    class Meta:
        ordering = ["order", "name"]


class Project(models.Model):
    """Portfolio projects"""

    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail_url = models.URLField(help_text="CDN URL for project thumbnail")
    github_link = models.URLField(blank=True)
    demo_link = models.URLField(blank=True)
    technologies = models.CharField(
        max_length=500, help_text="Comma-separated technologies"
    )
    order = models.IntegerField(
        default=0, help_text="Display order (lower numbers first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_technologies_list(self):
        """Return technologies as a list"""
        if self.technologies:
            return [
                tech.strip() for tech in self.technologies.split(",") if tech.strip()
            ]
        return []

    class Meta:
        ordering = ["order", "-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


# signals for cleaning up image files when a Blog is changed or removed


def _extract_media_paths_from_html(html_content):
    if not html_content:
        return set()

    media_url = settings.MEDIA_URL or "/media/"
    if not media_url.endswith("/"):
        media_url = f"{media_url}/"

    paths = set()
    for raw_url in re.findall(r'(?:src|href)=["\']([^"\']+)["\']', html_content):
        parsed_path = urlparse(raw_url).path
        if parsed_path.startswith(media_url):
            relative_path = parsed_path[len(media_url) :].lstrip("/")
            if relative_path:
                paths.add(relative_path)
    return paths


def _is_media_still_referenced(
    relative_path, exclude_aboutme_pk=None, exclude_blog_pk=None
):
    media_url = settings.MEDIA_URL or "/media/"
    if not media_url.endswith("/"):
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


def _delete_media_paths_if_unused(
    media_paths, exclude_aboutme_pk=None, exclude_blog_pk=None
):
    for path in media_paths:
        if _is_media_still_referenced(
            path,
            exclude_aboutme_pk=exclude_aboutme_pk,
            exclude_blog_pk=exclude_blog_pk,
        ):
            continue
        if default_storage.exists(path):
            default_storage.delete(path)


@receiver(pre_save, sender=Blog)
def cleanup_blog_on_save(sender, instance, **kwargs):
    """Delete old thumbnail and removed media files when Blog is saved.
    Also stores the old slug on the instance for post_save cache invalidation."""
    if not instance.pk:
        instance._old_slug = None
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._old_slug = None
        return

    # Store old slug so post_save can invalidate stale cache when slug changes
    instance._old_slug = old_instance.slug

    # Delete old thumbnail if it changed
    if (
        old_instance.thumbnail_img
        and old_instance.thumbnail_img != instance.thumbnail_img
    ):
        old_instance.thumbnail_img.delete(save=False)

    # Delete media files removed from content
    old_media = _extract_media_paths_from_html(old_instance.content)
    new_media = _extract_media_paths_from_html(instance.content)
    removed_media = old_media - new_media
    _delete_media_paths_if_unused(removed_media, exclude_blog_pk=instance.pk)


@receiver(post_delete, sender=Blog)
def cleanup_blog_on_delete(sender, instance, **kwargs):
    """Delete thumbnail and media files from Blog.content when Blog is deleted."""
    if instance.thumbnail_img:
        instance.thumbnail_img.delete(save=False)
    removed_media = _extract_media_paths_from_html(instance.content)
    _delete_media_paths_if_unused(removed_media)

    # Invalidate all related caches
    cache.delete("used_tags")
    cache.delete(f"blogpost_{instance.slug}")
    cache.delete_many(["latest_blogs", "total_blogs", "total_categories", "all_categories"])


@receiver(post_save, sender=Blog)
def invalidate_blog_cache_on_save(sender, instance, **kwargs):
    """Invalidate caches when a Blog post is created or updated."""
    cache.delete("used_tags")
    cache.delete(f"blogpost_{instance.slug}")
    # If slug was changed, also invalidate the old slug's cache to avoid stale responses
    old_slug = getattr(instance, "_old_slug", None)
    if old_slug and old_slug != instance.slug:
        cache.delete(f"blogpost_{old_slug}")
    cache.delete_many(["latest_blogs", "total_blogs", "total_categories", "all_categories"])


@receiver([post_save, post_delete], sender=Project)
def invalidate_project_cache(sender, instance, **kwargs):
    """Invalidate cache when a Project is created, updated, or deleted."""
    cache.delete_many(["total_projects", "all_projects"])


@receiver([post_save, post_delete], sender=Skill)
def invalidate_skill_cache(sender, instance, **kwargs):
    """Invalidate skills cache when a Skill is created, updated, or deleted."""
    cache.delete("all_skills")


@receiver(pre_save, sender=AboutMe)
def cleanup_aboutme_on_save(sender, instance, **kwargs):
    """Handle all file cleanup when AboutMe is saved.
    Combines bio media, profile image, hero image, and resume file cleanup
    into a single DB query instead of four separate ones."""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    # Delete media files removed from bio
    old_media = _extract_media_paths_from_html(old.bio)
    new_media = _extract_media_paths_from_html(instance.bio)
    removed_media = old_media - new_media
    _delete_media_paths_if_unused(removed_media, exclude_aboutme_pk=instance.pk)

    # Delete old profile image if changed
    if old.profile_img and old.profile_img != instance.profile_img:
        old.profile_img.delete(save=False)

    # Delete old hero image if changed
    if old.hero_img and old.hero_img != instance.hero_img:
        old.hero_img.delete(save=False)

    # Delete old resume file if changed
    if old.resume_file and old.resume_file != instance.resume_file:
        old.resume_file.delete(save=False)


@receiver(post_delete, sender=AboutMe)
def delete_aboutme_bio_media_on_delete(sender, instance, **kwargs):
    """Delete media files from AboutMe.bio on object delete when no longer used."""
    removed_media = _extract_media_paths_from_html(instance.bio)
    _delete_media_paths_if_unused(removed_media)
    if instance.profile_img:
        instance.profile_img.delete(save=False)
    if instance.hero_img:
        instance.hero_img.delete(save=False)
    if instance.resume_file:
        instance.resume_file.delete(save=False)


@receiver([post_save, post_delete], sender=AboutMe)
def invalidate_aboutme_cache(sender, instance, **kwargs):
    """Invalidate cache when AboutMe is updated."""
    cache.delete("about_me_singleton")
