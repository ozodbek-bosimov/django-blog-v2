import ipaddress
import operator
from functools import reduce

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q, Prefetch
from django.shortcuts import render
from django.templatetags.static import static

from home.models import AboutMe, Blog, Experience, ExperienceRole, Project, Skill

# Sentinel: distinguishes "key not in cache" from "key cached with value None".
# cache.get() returns None in both cases, so we pass this as the default instead.
_CACHE_MISS = object()


def _is_valid_ip(ip):
    """Validate if string is a valid IPv4 or IPv6 address using stdlib."""
    if not ip:
        return False
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def custom_404(request, exception=None):
    return render(request, "404.html", status=404)


def index(request):
    # 'about_me' is already injected by the about_me context processor,
    # but we still need the object locally to build absolute image URLs.
    about_me = cache.get("about_me_singleton", _CACHE_MISS)
    if about_me is _CACHE_MISS:
        about_me = AboutMe.objects.first()
        cache.set("about_me_singleton", about_me, 86400 * 30)

    abs_profile_image = ""
    abs_hero_image = ""
    hero_bg_image = (
        f"{request.scheme}://{request.get_host()}{static('images/banner.jpg')}"
    )

    if about_me:
        abs_profile_image = about_me.get_absolute_profile_image_url(request)
        abs_hero_image = about_me.get_absolute_hero_image_url(request)

        if abs_hero_image:
            hero_bg_image = abs_hero_image

    # Cache intensive numbers and homepage queries to save VPS CPU
    latest_blogs = cache.get_or_set(
        "latest_blogs", lambda: list(Blog.objects.order_by("-time", "-sno")[:3]), 86400
    )
    total_blogs = cache.get_or_set("total_blogs", lambda: Blog.objects.count(), 86400)
    total_projects = cache.get_or_set(
        "total_projects", lambda: Project.objects.count(), 86400
    )
    total_categories = cache.get_or_set(
        "total_categories",
        lambda: Blog.objects.values("category").distinct().count(),
        86400,
    )

    context = {
        # 'about_me' intentionally omitted — provided by the about_me context processor
        "abs_profile_image": abs_profile_image,
        "abs_hero_image": abs_hero_image,
        "hero_bg_image": hero_bg_image,
        "latest_blogs": latest_blogs,
        "total_blogs": total_blogs,
        "total_projects": total_projects,
        "total_categories": total_categories,
    }
    return render(request, "index.html", context)


def about(request):
    # Needed locally only to build the absolute profile image URL.
    about_me = cache.get("about_me_singleton", _CACHE_MISS)
    if about_me is _CACHE_MISS:
        about_me = AboutMe.objects.first()
        cache.set("about_me_singleton", about_me, 86400 * 30)

    # Skills rarely change — cache them for 24 hours.
    skills = cache.get_or_set("all_skills", lambda: list(Skill.objects.all()), 86400)

    # Experience entries — cache for 24 hours.
    experiences = cache.get_or_set(
        "all_experiences",
        lambda: list(
            Experience.objects.filter(roles__isnull=False)
            .distinct()
            .prefetch_related(
                Prefetch("roles", queryset=ExperienceRole.objects.order_by("-start_date"))
            )
        ),
        86400,
    )

    abs_profile_image = ""
    if about_me:
        abs_profile_image = about_me.get_absolute_profile_image_url(request)

    all_blogs = cache.get_or_set(
        "all_blogs_list",
        lambda: list(Blog.objects.order_by("-time", "-sno")),
        86400,
    )
    latest_blogs_about = all_blogs[:5]

    # 'about_me' intentionally omitted — provided by the about_me context processor
    context = {
        "skills": skills, 
        "experiences": experiences, 
        "abs_profile_image": abs_profile_image,
        "latest_blogs": latest_blogs_about
    }
    return render(request, "about.html", context)


def projects(request):
    projects = cache.get_or_set(
        "all_projects", lambda: list(Project.objects.all()), 86400
    )
    context = {"projects": projects}
    return render(request, "projects.html", context)


def blog(request):
    # Cache all blog posts for 24 hours; invalidated by post_save/post_delete signals.
    # Paginator slices the in-memory list — no extra DB queries per page.
    all_blogs = cache.get_or_set(
        "all_blogs_list",
        lambda: list(Blog.objects.order_by("-time", "-sno")),
        86400,
    )
    paginator = Paginator(all_blogs, 5)
    page = request.GET.get("page")
    blogs = paginator.get_page(page)
    context = {"blogs": blogs}
    return render(request, "blog.html", context)


def category(request, category):
    # Reuse the already-cached full blog list and filter in Python.
    # This avoids a per-category DB query while keeping a single cache key to invalidate.
    all_blogs = cache.get_or_set(
        "all_blogs_list",
        lambda: list(Blog.objects.order_by("-time", "-sno")),
        86400,
    )
    category_list = [b for b in all_blogs if b.category == category]

    if not category_list:
        message = f"No posts found in category: '{category}'"
        return render(
            request, "category.html", {"message": message, "category": category}
        )

    paginator = Paginator(category_list, 3)
    page = request.GET.get("page")
    category_posts = paginator.get_page(page)
    return render(
        request,
        "category.html",
        {"category": category, "category_posts": category_posts},
    )


def categories(request):
    all_categories = cache.get_or_set(
        "all_categories",
        lambda: list(
            Blog.objects.values("category")
            .annotate(count=Count("category"))
            .order_by("category")
        ),
        86400,
    )
    return render(request, "categories.html", {"all_categories": all_categories})


def search(request):
    # Rate limit: 20 requests per minute per IP
    ip = (
        (
            request.META.get("HTTP_X_FORWARDED_FOR", "")
            or request.META.get("REMOTE_ADDR", "")
        )
        .split(",")[0]
        .strip()
    )

    if ip and _is_valid_ip(ip):
        rl_key = f"search_rl_{ip}"
        try:
            req_count = cache.incr(rl_key)
        except ValueError:
            # Key doesn't exist yet — set it with a 60-second window.
            cache.set(rl_key, 1, 60)
            req_count = 1

        if req_count > 20:
            # Keep template expectations consistent: `results` should be a Page object
            # so pagination checks (`has_previous`/`has_next`) don't error.
            empty_page = Paginator(Blog.objects.none(), 3).get_page(1)
            return render(
                request,
                "search.html",
                {
                    "results": empty_page,
                    "query": "",
                    "message": "Too many requests. Please wait a moment and try again.",
                    "rate_limited": True,
                },
                status=429,
            )

    query = (request.GET.get("q") or "").strip()

    if query:
        query_list = query.split()
        q_objects = [
            Q(title__icontains=word) | Q(content__icontains=word) for word in query_list
        ]
        combined_q = reduce(operator.and_, q_objects)
        results = Blog.objects.filter(combined_q).distinct().order_by("-time", "-sno")
    else:
        results = Blog.objects.none()

    paginator = Paginator(results, 3)
    page = request.GET.get("page")
    results_page = paginator.get_page(page)

    if len(results_page) == 0:
        message = (
            "Sorry, no results found for your search query."
            if query
            else "Please enter a search query."
        )
        rate_limited = False
    else:
        message = ""
        rate_limited = False

    return render(
        request,
        "search.html",
        {
            "results": results_page,
            "query": query,
            "message": message,
            "rate_limited": rate_limited,
        },
    )


def blogpost(request, slug):
    try:
        blog_cache_key = f"blogpost_{slug}"
        blog = cache.get_or_set(
            blog_cache_key, lambda: Blog.objects.get(slug=slug), 86400
        )

        thumb = blog.get_absolute_thumbnail_url(request)

        # Build full blog URL for sharing
        blog_url = f"{request.scheme}://{request.get_host()}{request.path}"

        context = {"blog": blog, "abs_thumbnail": thumb, "blog_url": blog_url}
        return render(request, "blogpost.html", context)
    except Blog.DoesNotExist:
        context = {"message": "Blog post not found"}
        return render(request, "404.html", context, status=404)


"""
def leetcode_proxy(request):
    username = request.GET.get('username')
    if not username:
        return HttpResponse("Missing username", status=400)
    
    cache_key = f"leetcode_svg_{username}"
    cached_svg = cache.get(cache_key)
    if cached_svg:
        response = HttpResponse(cached_svg, content_type="image/svg+xml")
        response['Cache-Control'] = 'public, max-age=43200'
        return response
    
    url = f"https://leetcard.jacoblin.cool/{username}?font=Poppins&ext=heatmap&border=0&radius=0&theme=dark"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as api_response:
            svg_data = api_response.read().decode('utf-8')
            
            # Inject custom CSS to make the heatmap match the site's cyan theme perfectly
            custom_styles = '''
            <style>
                #background, #total-solved-bg, #total-solved-ring { fill: transparent !important; }
                #total-solved-bg, #easy-solved-bg, #medium-solved-bg, #hard-solved-bg, line:not([id*="-solved-"]) { stroke: #2d3748 !important; }
                rect[class^="ext-heatmap-"] { rx: 2px !important; ry: 2px !important; }
                #ext-heatmap-cells { opacity: 1 !important; }
                rect.ext-heatmap-0 { fill: #2d3748 !important; opacity: 1 !important; }
                rect.ext-heatmap-1 { fill: #164e63 !important; opacity: 1 !important; }
                rect.ext-heatmap-2 { fill: #0e7490 !important; opacity: 1 !important; }
                rect.ext-heatmap-3 { fill: #22d3ee !important; opacity: 1 !important; }
                rect.ext-heatmap-4 { fill: #67e8f9 !important; opacity: 1 !important; }
                rect[class^="ext-heatmap-"]:not(.ext-heatmap-0):not(.ext-heatmap-1):not(.ext-heatmap-2):not(.ext-heatmap-3):not(.ext-heatmap-4) { fill: #67e8f9 !important; opacity: 1 !important; }
                
                #username-text, #username { font-size: 16px !important; }
                #ranking { font-size: 12px !important; }
                #total-solved-text { font-size: 20px !important; }
                #easy-solved-type, #medium-solved-type, #hard-solved-type { font-size: 11px !important; }
                #easy-solved-count, #medium-solved-count, #hard-solved-count { font-size: 12px !important; }
                #ext-heatmap-from, #ext-heatmap-to { font-size: 8px !important; }
            </style>
            '''
            if '</svg>' in svg_data:
                svg_data = svg_data.replace('</svg>', custom_styles + '</svg>')
            
            cache.set(cache_key, svg_data, 43200) # cache for 12 hours
            
            response = HttpResponse(svg_data, content_type="image/svg+xml")
            response['Cache-Control'] = 'public, max-age=43200'
            return response
            
    except Exception as e:
        return HttpResponse('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="320"><rect width="100%" height="100%" fill="#0f172a"/><text x="50%" y="50%" fill="#9ca3af" text-anchor="middle" font-family="sans-serif">Failed to load LeetCode stats</text></svg>', content_type="image/svg+xml")
"""
