from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from home.models import Blog, AboutMe, Skill, Project

import random
import re


def index(request):
    random_blogs = Blog.objects.order_by('-time')[:3]
    context = {'random_blogs': random_blogs}
    return render(request, 'index.html', context)


def about(request):
    about_me = AboutMe.objects.first()
    skills = Skill.objects.all()
    context = {'about_me': about_me, 'skills': skills}
    return render(request, 'about.html', context)


def projects(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'projects.html', context)


def blog(request):
    blogs_qs = Blog.objects.all().order_by('-time')
    paginator = Paginator(blogs_qs, 3)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    context = {'blogs': blogs}
    return render(request, 'blog.html', context)


def category(request, category):
    category_qs = Blog.objects.filter(category=category).order_by('-time')
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
    query = (request.GET.get('q') or '').strip()

    if query:
        import operator
        from functools import reduce
        query_list = query.split()
        q_objects = [Q(title__icontains=word) | Q(content__icontains=word) for word in query_list]
        combined_q = reduce(operator.and_, q_objects)
        results = Blog.objects.filter(combined_q).distinct().order_by('-time')
    else:
        results = Blog.objects.none()

    paginator = Paginator(results, 3)
    page = request.GET.get('page')
    results_page = paginator.get_page(page)

    if len(results_page) == 0:
        message = "Sorry, no results found for your search query." if query else "Please enter a search query."
    else:
        message = ""

    # collect distinct used categories to show as tags in search UI
    used_tags = Blog.objects.values_list('category', flat=True).distinct().order_by('category')

    return render(
        request,
        'search.html',
        {'results': results_page, 'query': query, 'message': message, 'used_tags': used_tags},
    )


def blogpost(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        context = {'blog': blog}
        return render(request, 'blogpost.html', context)
    except Blog.DoesNotExist:
        context = {'message': 'Blog post not found'}
        return render(request, '404.html', context, status=404)

# def blogpost (request, slug):
#     blog = Blog.objects.filter(slug=slug).first()
#     context = {'blog': blog}
#     return render(request, 'blogpost.html', context)
