import operator
import re
from functools import reduce

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.templatetags.static import static

from home.models import Blog, AboutMe, Skill, Project


def _is_valid_ip(ip):
    """Validate if string is a valid IPv4 or IPv6 address."""
    if not ip:
        return False
    # Basic IPv4 validation
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        try:
            parts = [int(p) for p in ip.split('.')]
            return all(0 <= p <= 255 for p in parts)
        except ValueError:
            return False
    # IPv6 can have `:`
    return ':' in ip and not any(c in ip for c in [';', '"', "'"])


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


def index(request):
    about_me = AboutMe.objects.first()
    abs_profile_image = ''
    abs_hero_image = ''
    hero_bg_image = f"{request.scheme}://{request.get_host()}{static('images/banner.jpg')}"

    if about_me:
        profile_image = about_me.effective_profile_image
        if profile_image and not profile_image.startswith(('http://', 'https://')):
            abs_profile_image = f"{request.scheme}://{request.get_host()}{profile_image}"
        else:
            abs_profile_image = profile_image

        hero_image = about_me.effective_hero_image
        if hero_image and not hero_image.startswith(('http://', 'https://')):
            abs_hero_image = f"{request.scheme}://{request.get_host()}{hero_image}"
        else:
            abs_hero_image = hero_image

        if abs_hero_image:
            hero_bg_image = abs_hero_image

    # Cache intensive numbers and homepage queries to save VPS CPU
    random_blogs = cache.get_or_set('latest_blogs', lambda: list(Blog.objects.order_by('-time', '-sno')[:3]), 86400)
    total_blogs = cache.get_or_set('total_blogs', lambda: Blog.objects.count(), 86400)
    total_projects = cache.get_or_set('total_projects', lambda: Project.objects.count(), 86400)
    total_categories = cache.get_or_set('total_categories', lambda: Blog.objects.values('category').distinct().count(), 86400)

    context = {
        'about_me': about_me,
        'abs_profile_image': abs_profile_image,
        'abs_hero_image': abs_hero_image,
        'hero_bg_image': hero_bg_image,
        'random_blogs': random_blogs,
        'total_blogs': total_blogs,
        'total_projects': total_projects,
        'total_categories': total_categories,
    }
    return render(request, 'index.html', context)


def about(request):
    about_me = AboutMe.objects.first()
    skills = Skill.objects.all()
    abs_profile_image = ''
    if about_me:
        img = about_me.effective_profile_image
        if img and not img.startswith(('http://', 'https://')):
            abs_profile_image = f"{request.scheme}://{request.get_host()}{img}"
        else:
            abs_profile_image = img
    context = {'about_me': about_me, 'skills': skills, 'abs_profile_image': abs_profile_image}
    return render(request, 'about.html', context)


def projects(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'projects.html', context)


def blog(request):
    blogs_qs = Blog.objects.all().order_by('-time', '-sno')
    paginator = Paginator(blogs_qs, 3)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    context = {'blogs': blogs}
    return render(request, 'blog.html', context)


def category(request, category):
    category_qs = Blog.objects.filter(category=category).order_by('-time', '-sno')
    if not category_qs.exists():
        message = f"No posts found in category: '{category}'"
        return render(request, "category.html", {"message": message, "category": category})

    paginator = Paginator(category_qs, 3)
    page = request.GET.get('page')
    category_posts = paginator.get_page(page)
    return render(
        request,
        "category.html",
        {"category": category, 'category_posts': category_posts},
    )


def categories(request):
    all_categories = Blog.objects.values('category').distinct().order_by('category')
    return render(request, "categories.html", {'all_categories': all_categories})


def search(request):
    # Rate limit: 20 requests per minute per IP
    ip = (
        request.META.get('HTTP_X_FORWARDED_FOR', '')
        or request.META.get('REMOTE_ADDR', '')
    ).split(',')[0].strip()

    if ip and _is_valid_ip(ip):
        rl_key = f"search_rl_{ip}"
        try:
            req_count = cache.incr(rl_key)
        except ValueError:
            # Key doesn't exist, set it to 1
            cache.set(rl_key, 1, 60)
            req_count = 1

        if req_count > 20:
            # Keep template expectations consistent: `results` should be a Page object
            # so pagination checks (`has_previous`/`has_next`) don't error.
            empty_page = Paginator(Blog.objects.none(), 3).get_page(1)
            return render(request, 'search.html', {
                'results': empty_page,
                'query': '',
                'message': 'Too many requests. Please wait a moment and try again.',
                'rate_limited': True,
            }, status=429)

    query = (request.GET.get('q') or '').strip()

    if query:
        query_list = query.split()
        q_objects = [Q(title__icontains=word) | Q(content__icontains=word) for word in query_list]
        combined_q = reduce(operator.and_, q_objects)
        results = Blog.objects.filter(combined_q).distinct().order_by('-time', '-sno')
    else:
        results = Blog.objects.none()

    paginator = Paginator(results, 3)
    page = request.GET.get('page')
    results_page = paginator.get_page(page)

    if len(results_page) == 0:
        message = "Sorry, no results found for your search query." if query else "Please enter a search query."
        rate_limited = False
    else:
        message = ""
        rate_limited = False

    return render(
        request,
        'search.html',
        {'results': results_page, 'query': query, 'message': message, 'rate_limited': rate_limited},
    )


def blogpost(request, slug):
    try:
        blog_cache_key = f"blogpost_{slug}"
        blog = cache.get_or_set(blog_cache_key, lambda: Blog.objects.get(slug=slug), 86400)

        thumb = blog.effective_thumbnail
        if thumb and not thumb.startswith(('http://', 'https://')):
            thumb = f"{request.scheme}://{request.get_host()}{thumb}"

        # Build full blog URL for sharing
        blog_url = f"{request.scheme}://{request.get_host()}{request.path}"

        context = {'blog': blog, 'abs_thumbnail': thumb, 'blog_url': blog_url}
        return render(request, 'blogpost.html', context)
    except Blog.DoesNotExist:
        context = {'message': 'Blog post not found'}
        return render(request, '404.html', context, status=404)
