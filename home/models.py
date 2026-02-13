from django.db import models

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
