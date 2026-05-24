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
    """Transform iframes to use data-src instead of src.
    
    This completely prevents the browser from making eager network requests,
    which is crucial for performance on mobile devices with many embeds.
    JS will handle IntersectionObserver to load them on demand.
    """
    if not content or "<iframe" not in content.lower():
        return content

    def _process(match):
        full_tag = match.group(0)
        
        # Add class for our custom JS and CSS to target
        if 'class="' in full_tag:
            full_tag = re.sub(r'class="([^"]*)"', r'class="\1 lazy-iframe-custom"', full_tag, 1)
        else:
            full_tag = full_tag.replace('<iframe', '<iframe class="lazy-iframe-custom"', 1)
            
        # Replace src="..." with data-src="..." (but not data-src or other *-src)
        full_tag = re.sub(r'(?<![a-zA-Z-])src\s*=\s*(["\'])(.*?)\1', r'data-src="\2"', full_tag, flags=re.IGNORECASE)
        
        return full_tag

    result = re.sub(r"<iframe\b[^>]*>", _process, content, flags=re.IGNORECASE)
    return mark_safe(result)

