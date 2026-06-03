"""Management command to migrate images to media/postimages/.

Moves image files from both media/ root (CKEditor uploads) and
media/images/ (old thumbnail path) into media/postimages/, then updates
every HTML reference in Blog.content and AboutMe.bio so existing posts
keep working.

Usage:
    python manage.py migrate_media_to_postimages          # dry-run (preview)
    python manage.py migrate_media_to_postimages --apply  # actually do it
"""

import os
import re
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

# Image extensions that CKEditor typically uploads
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".svg",
    ".tiff",
    ".ico",
}

# Subdirectories that already have a purpose — never touch these
SKIP_DIRS = {"hero", "profile", "resume", "postimages"}


class Command(BaseCommand):
    help = (
        "Move image files from media/ root and media/images/ into "
        "media/postimages/ and update HTML references in Blog.content "
        "and AboutMe.bio."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Actually move files and update the database. "
            "Without this flag the command only prints what it would do (dry-run).",
        )

    def handle(self, *args, **options):
        apply = options["apply"]
        media_root = settings.MEDIA_ROOT
        dest_dir = os.path.join(media_root, "postimages")

        if apply:
            os.makedirs(dest_dir, exist_ok=True)

        # ------------------------------------------------------------------
        # 1. Find image files sitting directly in media/ root
        # ------------------------------------------------------------------
        files_to_move = []
        for entry in os.listdir(media_root):
            full_path = os.path.join(media_root, entry)
            if not os.path.isfile(full_path):
                continue
            _, ext = os.path.splitext(entry)
            if ext.lower() in IMAGE_EXTENSIONS:
                files_to_move.append(entry)

        if files_to_move:
            self.stdout.write(
                self.style.WARNING(
                    f"\n📁 Found {len(files_to_move)} image(s) in media/ root:"
                )
            )
            for f in sorted(files_to_move):
                self.stdout.write(f"   media/{f}  →  media/postimages/{f}")
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✅ No images to move in media/ root.")
            )

        # ------------------------------------------------------------------
        # 2. Move files (if --apply)
        # ------------------------------------------------------------------
        moved_count = 0
        if apply and files_to_move:
            for f in files_to_move:
                src = os.path.join(media_root, f)
                dst = os.path.join(dest_dir, f)
                if os.path.exists(dst):
                    self.stdout.write(
                        self.style.WARNING(
                            f"   ⚠️  {f} already exists in postimages/ — "
                            "deleting only from root"
                        )
                    )
                    os.remove(src)
                else:
                    shutil.move(src, dst)
                moved_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ {moved_count} file(s) moved from media/ root."
                )
            )

        # ------------------------------------------------------------------
        # 3. Move files from media/images/ to media/postimages/
        # ------------------------------------------------------------------
        images_dir = os.path.join(media_root, "images")
        images_files = []
        if os.path.isdir(images_dir):
            for entry in os.listdir(images_dir):
                full_path = os.path.join(images_dir, entry)
                if not os.path.isfile(full_path):
                    continue
                _, ext = os.path.splitext(entry)
                if ext.lower() in IMAGE_EXTENSIONS:
                    images_files.append(entry)

        if images_files:
            self.stdout.write(
                self.style.WARNING(
                    f"\n📁 Found {len(images_files)} image(s) in media/images/:"
                )
            )
            for f in sorted(images_files):
                self.stdout.write(f"   media/images/{f}  →  media/postimages/{f}")
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✅ No images to move in media/images/.")
            )

        images_moved = 0
        if apply and images_files:
            for f in images_files:
                src = os.path.join(images_dir, f)
                dst = os.path.join(dest_dir, f)
                if os.path.exists(dst):
                    self.stdout.write(
                        self.style.WARNING(
                            f"   ⚠️  {f} already exists in postimages/ — "
                            "deleting only from images/"
                        )
                    )
                    os.remove(src)
                else:
                    shutil.move(src, dst)
                images_moved += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ {images_moved} file(s) moved from media/images/."
                )
            )
            # Remove empty images/ directory
            try:
                os.rmdir(images_dir)
                self.stdout.write(
                    self.style.SUCCESS("   📂 Removed empty media/images/ folder.")
                )
            except OSError:
                pass  # directory not empty (has non-image files)

        # ------------------------------------------------------------------
        # 4. Find and update DB references
        # ------------------------------------------------------------------
        from home.models import AboutMe, Blog

        media_url = settings.MEDIA_URL.rstrip("/")  # e.g. "/media"

        # Pattern 1: /media/FILENAME (root files, not in any subdir)
        pattern_root = re.compile(
            rf"({re.escape(media_url)}/)"
            rf"(?!(?:{'|'.join(SKIP_DIRS)})/)"
            rf'([^"\'\s>/]+)'
        )

        # Pattern 2: /media/images/FILENAME → /media/postimages/FILENAME
        pattern_images = re.compile(rf'({re.escape(media_url)}/)images/([^"\'\s>]+)')

        def replace_refs(html):
            """Replace /media/file.jpg and /media/images/file.jpg → /media/postimages/file.jpg"""
            html = pattern_images.sub(r"\1postimages/\2", html)
            html = pattern_root.sub(r"\1postimages/\2", html)
            return html

        # --- Blog.content ---
        blog_updates = []
        for blog in Blog.objects.all():
            new_content = replace_refs(blog.content)
            if new_content != blog.content:
                blog_updates.append((blog, new_content))

        # --- AboutMe.bio ---
        aboutme_updates = []
        for about in AboutMe.objects.all():
            new_bio = replace_refs(about.bio)
            if new_bio != about.bio:
                aboutme_updates.append((about, new_bio))

        if blog_updates or aboutme_updates:
            msg = f"\n📝 DB updates: {len(blog_updates)} blog post(s), {len(aboutme_updates)} aboutme"
            self.stdout.write(self.style.WARNING(msg))
            for blog, _new_content in blog_updates:
                self.stdout.write(
                    f"   Blog #{blog.sno} [{blog.title[:40]}]: reference will be updated"
                )

            for about, _new_bio in aboutme_updates:
                self.stdout.write(
                    f"   AboutMe [{about.name[:40]}]: reference will be updated"
                )
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ No DB references to update."))

        # ------------------------------------------------------------------
        # 5. Apply DB changes (if --apply)
        # ------------------------------------------------------------------
        if apply and (blog_updates or aboutme_updates):
            for blog, new_content in blog_updates:
                blog.content = new_content
                Blog.objects.filter(pk=blog.pk).update(content=new_content)

            for about, new_bio in aboutme_updates:
                about.bio = new_bio
                AboutMe.objects.filter(pk=about.pk).update(bio=new_bio)

            self.stdout.write(self.style.SUCCESS("✅ DB references updated."))

        # ------------------------------------------------------------------
        # 6. Summary
        # ------------------------------------------------------------------
        has_work = files_to_move or images_files or blog_updates or aboutme_updates
        if not apply and has_work:
            self.stdout.write(
                self.style.NOTICE(
                    "\n⚡ This was a dry run. To apply changes:\n"
                    "   python manage.py migrate_media_to_postimages --apply\n"
                )
            )
        elif apply:
            self.stdout.write(self.style.SUCCESS("\n🎉 All done!"))
