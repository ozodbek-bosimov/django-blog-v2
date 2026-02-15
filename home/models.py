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
