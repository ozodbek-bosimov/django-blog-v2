import operator
from functools import reduce

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from home.models import Blog, AboutMe, Skill, Project


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


def index(request):
    random_blogs = Blog.objects.order_by('-time', '-sno')[:3]
    context = {'random_blogs': random_blogs}
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
    if ip:
        rl_key = f"search_rl_{ip}"
        req_count = cache.get(rl_key, 0)
        if req_count >= 20:
            return render(request, 'search.html', {
                'results': [],
                'query': '',
                'message': 'Too many requests. Please wait a moment and try again.',
            })
        cache.set(rl_key, req_count + 1, 60)

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
    else:
        message = ""

    return render(
        request,
        'search.html',
        {'results': results_page, 'query': query, 'message': message},
    )


def blogpost(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        thumb = blog.effective_thumbnail
        if thumb and not thumb.startswith(('http://', 'https://')):
            thumb = f"{request.scheme}://{request.get_host()}{thumb}"
        context = {'blog': blog, 'abs_thumbnail': thumb}
        return render(request, 'blogpost.html', context)
    except Blog.DoesNotExist:
        context = {'message': 'Blog post not found'}
        return render(request, '404.html', context, status=404)
