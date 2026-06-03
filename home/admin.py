import re
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget

from home.models import (
    AboutMe,
    Blog,
    Experience,
    ExperienceRole,
    Project,
    Skill,
    SharedFile,
)


def _sanitize_youtube_embeds(html_content):
    """Convert YouTube watch/short URLs to embed URLs and ensure proper iframe attributes.
    Shared by BlogAdminForm.clean_content() and AboutMeAdminForm.clean_bio()."""
    if not html_content:
        return html_content

    def time_to_seconds(time_str):
        if not time_str:
            return None
        time_str = time_str.strip()
        if time_str.isdigit():
            return int(time_str)
        match = re.match(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$", time_str)
        if not match:
            return None
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total = (hours * 3600) + (minutes * 60) + seconds
        return total if total > 0 else None

    def build_embed_url(video_id, time_str):
        base = f"https://www.youtube.com/embed/{video_id}"
        start_seconds = time_to_seconds(time_str)
        if start_seconds is None:
            return base
        return f"{base}?start={start_seconds}"

    def add_rel_param(url):
        if "rel=" in url:
            return url
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}rel=0"

    def ensure_iframe_attr(tag, attr, value=None):
        if attr == "allowfullscreen":
            if re.search(r"\ballowfullscreen\b", tag, re.IGNORECASE):
                return tag
            return tag[:-1] + " allowfullscreen>"
        if re.search(rf"\b{attr}\s*=", tag, re.IGNORECASE):
            return tag
        return tag[:-1] + f' {attr}="{value}">'

    # Convert watch URLs to embed URLs (for media plugin)
    html_content = re.sub(
        r"https://www\.youtube\.com/watch\?v=([a-zA-Z0-9_-]+)(?:&t=([0-9hms]+))?",
        lambda match: build_embed_url(match.group(1), match.group(2)),
        html_content,
    )

    # Also handle youtu.be short URLs
    html_content = re.sub(
        r"https://youtu\.be/([a-zA-Z0-9_-]+)(?:\?t=([0-9hms]+))?",
        lambda match: build_embed_url(match.group(1), match.group(2)),
        html_content,
    )

    # Normalize embed URLs that use ?t=
    html_content = re.sub(
        r"https://www\.youtube\.com/embed/([a-zA-Z0-9_-]+)\?t=([0-9hms]+)",
        lambda match: build_embed_url(match.group(1), match.group(2)),
        html_content,
    )

    # Ensure rel=0 for YouTube embed URLs
    html_content = re.sub(
        r'https://www\.youtube\.com/embed/[a-zA-Z0-9_-]+(?:\?[^"\s>]*)?',
        lambda match: add_rel_param(match.group(0)),
        html_content,
    )

    # Ensure iframe attributes needed for YouTube playback
    def augment_iframe(match):
        tag = match.group(0)
        if "youtube.com/embed" not in tag:
            return tag
        tag = ensure_iframe_attr(
            tag,
            "allow",
            "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
        )
        tag = ensure_iframe_attr(
            tag, "referrerpolicy", "strict-origin-when-cross-origin"
        )
        tag = ensure_iframe_attr(tag, "title", "YouTube video player")
        tag = ensure_iframe_attr(tag, "frameborder", "0")
        tag = ensure_iframe_attr(tag, "allowfullscreen")
        return tag

    html_content = re.sub(
        r"<iframe[^>]*>", augment_iframe, html_content, flags=re.IGNORECASE
    )
    return html_content


# Register your models here.
class BlogAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name="default"))
    meta = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 3, "style": "width:100%; resize:vertical;", "maxlength": 600}
        ),
        max_length=600,
        help_text="Max 600 characters. This text appears in search results and social media previews.",
    )

    class Meta:
        model = Blog
        fields = "__all__"

    def clean_thumbnail_img(self):
        img = self.cleaned_data.get("thumbnail_img")
        if img and hasattr(img, "size") and img.size > 10 * 1024 * 1024:
            size_mb = img.size / (1024 * 1024)
            raise forms.ValidationError(
                f"Image size is {size_mb:.1f} MB — maximum allowed size is 10 MB. "
                "Please choose a smaller file."
            )
        return img

    def clean_content(self):
        """Convert YouTube watch URLs to embed URLs and ensure proper iframe format"""
        content = self.cleaned_data.get("content", "")

        # Check content size - 5MB limit
        content_size_bytes = len(content.encode("utf-8"))
        max_size_bytes = 5 * 1024 * 1024  # 5MB
        if content_size_bytes > max_size_bytes:
            size_mb = content_size_bytes / (1024 * 1024)
            raise forms.ValidationError(
                f"Blog post content is too large ({size_mb:.1f} MB). "
                "Maximum allowed size is 5 MB. Please reduce the content size."
            )

        return _sanitize_youtube_embeds(content)

    def clean_meta(self):
        meta = (self.cleaned_data.get("meta") or "").strip()
        if len(meta) > 600:
            raise forms.ValidationError("Meta text can be at most 600 characters.")
        return meta


class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm

    class Media:
        js = ("js/admin_thumbnail.js", "js/admin_ckeditor_fix.js")

    list_display = ["title", "topic", "created_at_display", "slug"]
    list_filter = ["topic"]
    search_fields = ["title", "topic", "slug"]
    readonly_fields = ("thumbnail_preview",)
    fieldsets = (
        (None, {"fields": ("title", "meta", "content", "topic", "slug")}),
        ("Meta", {"fields": ("time",)}),
        (
            "Thumbnail",
            {"fields": ("thumbnail_img", "thumbnail_url", "thumbnail_preview")},
        ),
    )

    @admin.display(description="Created", ordering="time")
    def created_at_display(self, obj):
        return timezone.localtime(obj.time).strftime("%Y-%m-%d  %H:%M")

    @admin.display(description="Current thumbnail")
    def thumbnail_preview(self, obj):
        if obj.thumbnail_img:
            return format_html(
                '<img src="{}" style="max-width: 200px; height: auto;" />',
                escape(obj.thumbnail_img.url),
            )
        elif obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="max-width: 200px; height: auto;" />',
                escape(obj.thumbnail_url),
            )
        return "(No image)"


admin.site.register(Blog, BlogAdmin)


class AboutMeAdminForm(forms.ModelForm):
    bio = forms.CharField(widget=CKEditor5Widget(config_name="default"))

    class Meta:
        model = AboutMe
        fields = "__all__"

    def clean_bio(self):
        """Check bio content size limit and sanitize YouTube embeds"""
        bio = self.cleaned_data.get("bio", "")
        bio_size_bytes = len(bio.encode("utf-8"))
        max_size_bytes = 5 * 1024 * 1024  # 5MB
        if bio_size_bytes > max_size_bytes:
            size_mb = bio_size_bytes / (1024 * 1024)
            raise forms.ValidationError(
                f"Bio content is too large ({size_mb:.1f} MB). "
                "Maximum allowed size is 5 MB. Please reduce the content size."
            )
        return _sanitize_youtube_embeds(bio)

    def clean_profile_img(self):
        img = self.cleaned_data.get("profile_img")
        if img and hasattr(img, "size") and img.size > 10 * 1024 * 1024:
            size_mb = img.size / (1024 * 1024)
            raise forms.ValidationError(
                f"Image size is {size_mb:.1f} MB — maximum allowed size is 10 MB. "
                "Please choose a smaller file."
            )
        return img

    def clean_hero_img(self):
        img = self.cleaned_data.get("hero_img")
        if img and hasattr(img, "size") and img.size > 10 * 1024 * 1024:
            size_mb = img.size / (1024 * 1024)
            raise forms.ValidationError(
                f"Image size is {size_mb:.1f} MB — maximum allowed size is 10 MB. "
                "Please choose a smaller file."
            )
        return img


class AboutMeAdmin(admin.ModelAdmin):
    """Admin for singleton AboutMe model"""

    form = AboutMeAdminForm

    class Media:
        js = ("js/admin_ckeditor_fix.js",)

    readonly_fields = ("profile_image_preview", "hero_image_preview")
    fieldsets = (
        ("Personal Info", {"fields": ("name", "profession", "email", "phone")}),
        ("About", {"fields": ("bio",)}),
        ("Resume", {"fields": ("resume_file", "resume_url")}),
        (
            "Profile Image",
            {"fields": ("profile_img", "profile_image_url", "profile_image_preview")},
        ),
        (
            "Hero Background",
            {"fields": ("hero_img", "hero_image_url", "hero_image_preview")},
        ),
        (
            "Social Links",
            {
                "fields": (
                    "linkedin_url",
                    "github_url",
                    "telegram_url",
                    "x_url",
                    "leetcode_url",
                    "youtube_url",
                    "instagram_url",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        """Limit to one instance only"""
        if AboutMe.objects.exists():
            return False
        return super().has_add_permission(request)

    @admin.display(description="Profile Image Preview")
    def profile_image_preview(self, obj):
        if obj:
            url = obj.effective_profile_image
            if url:
                return format_html(
                    '<img src="{}" style="max-width: 200px; '
                    'height: auto; border-radius: 50%;" />',
                    escape(url),
                )
        return "(No image)"

    @admin.display(description="Hero Background Preview")
    def hero_image_preview(self, obj):
        if obj:
            url = obj.effective_hero_image
            if url:
                return format_html(
                    '<img src="{}" style="max-width: 320px; width: 100%; '
                    'height: auto; border-radius: 16px;" />',
                    escape(url),
                )
        return "(No image)"


class SkillAdmin(admin.ModelAdmin):
    """Admin for Skill model"""

    class SkillAdminForm(forms.ModelForm):
        class Meta:
            model = Skill
            fields = "__all__"
            help_texts = {
                "percentage": (
                    "0-19% → Familiar, 20-39% → Basic, 40-69% → Working Knowledge, "
                    "70-89% → Advanced, 90-100% → Expert"
                ),
            }

    form = SkillAdminForm
    list_display = ["name", "percentage", "order"]
    list_editable = ["order"]
    list_filter = ["percentage"]
    search_fields = ["name"]


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    def clean_thumbnail_img(self):
        img = self.cleaned_data.get("thumbnail_img")
        if img and hasattr(img, "size") and img.size > 10 * 1024 * 1024:
            size_mb = img.size / (1024 * 1024)
            raise forms.ValidationError(
                f"Image size is {size_mb:.1f} MB — maximum allowed size is 10 MB. "
                "Please choose a smaller file."
            )
        return img


class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project model"""

    form = ProjectAdminForm
    list_display = ["title", "order", "created_at"]
    list_editable = ["order"]
    readonly_fields = ("thumbnail_preview", "created_at")
    fieldsets = (
        ("Basic Info", {"fields": ("title", "description")}),
        (
            "Thumbnail",
            {"fields": ("thumbnail_img", "thumbnail_url", "thumbnail_preview")},
        ),
        ("Links", {"fields": ("github_link", "demo_link")}),
        ("Technical", {"fields": ("technologies",)}),
        ("Meta", {"fields": ("order", "created_at")}),
    )
    search_fields = ["title", "description", "technologies"]

    @admin.display(description="Thumbnail Preview")
    def thumbnail_preview(self, obj):
        if obj:
            url = obj.effective_thumbnail
            if url:
                return format_html(
                    '<img src="{}" style="max-width: 200px; height: auto;" />',
                    escape(url),
                )
        return "(No image)"


class LogEntryAdmin(admin.ModelAdmin):
    change_list_template = "admin/logentry_change_list.html"
    date_hierarchy = "action_time"
    list_display = ["action_time", "user", "content_type", "object_repr", "action_flag"]
    list_filter = ["action_flag", "user", "content_type"]
    search_fields = ["object_repr", "change_message", "user__username"]
    ordering = ["-action_time"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "prune/",
                self.admin_site.admin_view(self.prune_old_logs_view),
                name="admin_logentry_prune",
            ),
        ]
        return custom_urls + urls

    def _changelist_url(self):
        opts = self.model._meta
        return reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["prune_url"] = reverse("admin:admin_logentry_prune")
        extra_context["retention_days"] = str(
            max(
                int(getattr(settings, "ADMIN_LOG_RETENTION_DAYS", 90)),
                1,
            )
        )
        return super().changelist_view(request, extra_context=extra_context)

    def prune_old_logs_view(self, request):
        if request.method != "POST":
            return redirect(self._changelist_url())

        retention_days_raw = request.POST.get("days")
        if retention_days_raw:
            try:
                retention_days = max(int(retention_days_raw), 1)
            except (TypeError, ValueError):
                self.message_user(
                    request,
                    "Days must be a whole number greater than or equal to 1.",
                    level=messages.ERROR,
                )
                return redirect(self._changelist_url())
        else:
            retention_days = max(
                int(getattr(settings, "ADMIN_LOG_RETENTION_DAYS", 90)), 1
            )

        cutoff = timezone.now() - timedelta(days=retention_days)
        deleted_count, _ = LogEntry.objects.filter(action_time__lt=cutoff).delete()

        self.message_user(
            request,
            f"Deleted {deleted_count} admin history rows older than {retention_days} days.",
            level=messages.SUCCESS,
        )
        return redirect(self._changelist_url())


class ExperienceRoleInline(admin.StackedInline):
    """Inline for positions/roles within one company.
    One role = single-position experience, 2+ roles = multi-position."""

    model = ExperienceRole
    extra = 0  # show zero extra blank role forms (min_num will force 1 for new objects)
    min_num = 1
    validate_min = True
    fieldsets = (
        (None, {"fields": ("position", "employment_type", "work_type", "location")}),
        ("Duration", {"fields": ("start_date", "end_date", "is_current")}),
        ("Details", {"fields": ("description",)}),
    )


class ExperienceAdmin(admin.ModelAdmin):
    """Admin for Experience model — roles-only approach.

    Every experience uses the ExperienceRole inline exclusively:
      • 1 role  → renders as a single-position entry on the site.
      • 2+ roles → renders as a multi-role (grouped) entry.
    No separate 'Single position' section exists.
    """

    class Media:
        css = {"all": ("css/admin_experience.css",)}

    list_display = ["company", "entry_type", "order"]
    list_editable = ["order"]
    search_fields = ["company"]
    inlines = [ExperienceRoleInline]
    fieldsets = (
        (
            "Company",
            {
                "fields": (
                    "company",
                    "company_url",
                    "company_logo",
                    "company_logo_url",
                    "order",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("roles")

    @admin.display(description="Type")
    def entry_type(self, obj):
        role_count = obj.roles.count()
        if role_count > 1:
            return format_html(
                '<span style="color:#22d3ee">{} roles</span>', role_count
            )
        if role_count == 1:
            role = obj.roles.first()
            return format_html('<span style="color:#94a3b8">{}</span>', role.position)
        return mark_safe('<span style="color:#ef4444">\u2014 empty \u2014</span>')


admin.site.register(AboutMe, AboutMeAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(LogEntry, LogEntryAdmin)


@admin.register(SharedFile)
class SharedFileAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "uploaded_at", "copy_url_button")
    search_fields = ("name", "file")
    readonly_fields = ("uploaded_at",)

    @admin.display(description="Copy URL")
    def copy_url_button(self, obj):
        if obj.file and hasattr(obj.file, "url"):
            return format_html(
                "<a class=\"button\" style=\"cursor: pointer; color: white;\" onclick=\"navigator.clipboard.writeText(window.location.origin + '{}'); this.innerText='Copied!'; setTimeout(() => this.innerText='Copy URL', 2000);\">Copy URL</a>",
                escape(obj.file.url),
            )
        return ""


# Custom ordering for models in the admin panel
def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

    ordering = {
        "About Me": 1,
        "Experiences": 2,
        "Projects": 3,
        "Skills": 4,
        "Blogs": 5,
        "Shared Files": 6,
    }

    for app in app_list:
        if app["app_label"] == "home":
            app["models"].sort(key=lambda x: ordering.get(x["name"], 999))

    return app_list


admin.site.get_app_list = get_app_list.__get__(admin.site, admin.site.__class__)
