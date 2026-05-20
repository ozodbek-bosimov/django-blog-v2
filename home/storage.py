"""Custom file storage for CKEditor 5 uploads.

Routes all CKEditor inline image uploads into the ``postimages/`` sub-directory
under ``MEDIA_ROOT`` so they are co-located with Blog thumbnail images and
don't clutter the media root.
"""

from django.core.files.storage import FileSystemStorage


class CKEditor5Storage(FileSystemStorage):
    """FileSystemStorage subclass that prepends ``postimages/`` to every saved
    file name, keeping CKEditor uploads organised alongside blog post images."""

    def save(self, name, content, max_length=None):
        # Ensure the file is placed under the postimages/ subdirectory
        if not name.startswith("postimages/"):
            name = f"postimages/{name}"
        return super().save(name, content, max_length=max_length)
