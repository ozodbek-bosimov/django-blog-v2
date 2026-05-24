import re
import math

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="reading_time")
def reading_time(content):
    """Return estimated reading time in minutes for HTML content."""
    if not content:
        return 1
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", content)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Count words
    word_count = len(text.split()) if text else 0
    # Average reading speed: 160 words per minute
    minutes = max(1, math.ceil(word_count / 160))
    return minutes


# Regex to match <iframe ...> tags (self-closing or not)
_IFRAME_RE = re.compile(r"(<iframe\b)", re.IGNORECASE)
_IFRAME_SRC_RE = re.compile(
    r"(<iframe\b[^>]*?)\bsrc\s*=\s*([\"'])(.*?)\2", re.IGNORECASE | re.DOTALL
)


@register.filter(name="lazy_iframes")
def lazy_iframes(content):
    """Replace iframe src with data-src so the browser never eagerly loads them.

    This runs server-side, before the HTML reaches the browser. The companion
    JavaScript (blogpost.js) restores src via IntersectionObserver on desktop
    or click-to-load on mobile.

    Each iframe gets:
      - src removed, value moved to data-src
      - class="lazy-iframe" added
      - loading="lazy" added
    """
    if not content:
        return content

    def _replace_iframe(match):
        prefix = match.group(1)  # <iframe ... (before src)
        quote = match.group(2)  # quote character (' or ")
        src_value = match.group(3)  # actual URL

        # Build the replacement: data-src instead of src
        result = prefix

        # Add class="lazy-iframe" — merge with existing class if present
        if re.search(r'\bclass\s*=', result, re.IGNORECASE):
            # Append to existing class attribute
            result = re.sub(
                r'(\bclass\s*=\s*["\'])([^"\']*)',
                r'\1\2 lazy-iframe',
                result,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            result += ' class="lazy-iframe"'

        # Add loading="lazy" if not already present
        if not re.search(r'\bloading\s*=', result, re.IGNORECASE):
            result += ' loading="lazy"'

        # Add data-src with the original URL (instead of src)
        result += " data-src=" + quote + src_value + quote

        return result

    processed = _IFRAME_SRC_RE.sub(_replace_iframe, content)
    return mark_safe(processed)

