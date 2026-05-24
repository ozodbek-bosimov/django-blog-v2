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


@register.filter(name="lazy_iframes")
def lazy_iframes(content):
    """Add loading="lazy" to every <iframe> so the browser defers off-screen ones.

    This is a simple, native-browser solution. The browser will only load
    iframes that are near the viewport and defer the rest automatically.
    No JavaScript required.
    """
    if not content or "<iframe" not in content.lower():
        return content

    def _process(match):
        full_tag = match.group(0)
        # Skip if already has loading attribute
        if re.search(r'\bloading\s*=', full_tag, re.IGNORECASE):
            return full_tag
        # Insert loading="lazy" right after "<iframe"
        return "<iframe" + ' loading="lazy"' + full_tag[7:]

    result = re.sub(r"<iframe\b[^>]*>", _process, content, flags=re.IGNORECASE)
    return mark_safe(result)
