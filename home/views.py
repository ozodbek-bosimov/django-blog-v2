from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from home.models import Blog, AboutMe, Skill, Project

import random
import re


def index(request):
    blogs = list(Blog.objects.all())
    sample_size = min(3, len(blogs))
    random_blogs = random.sample(blogs, sample_size) if sample_size > 0 else []
    context = {'random_blogs': random_blogs}
    return render(request, 'index.html', context)


def about(request):
    about_me = AboutMe.objects.first()
    skills = Skill.objects.all()
    context = {'about_me': about_me, 'skills': skills}
    return render(request, 'about.html', context)


def thanks(request):
    return render(request, 'thanks.html')


def contact(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        message_text = (request.POST.get('message') or '').strip()

        if not name or not email or not phone or not message_text:
            messages.error(request, 'One or more fields are empty!')
        else:
            email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            # Allow international phone numbers: optional +, 9–15 digits
            phone_pattern = re.compile(r'^\+?[0-9]{9,15}$')

            if email_pattern.match(email) and phone_pattern.match(phone):
                form_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'message': message_text,
                }
                body = '''
From:    {}
Message: {}
Email:   {}
Phone:   {}
'''.format(
                    form_data['name'],
                    form_data['message'],
                    form_data['email'],
                    form_data['phone'],
                )

                recipient = getattr(settings, 'EMAIL_HOST_USER', None)
                if recipient:
                    send_mail(
                        subject='You got a mail!',
                        message=body,
                        from_email=recipient,
                        recipient_list=[recipient],
                        fail_silently=True,
                    )
                messages.success(request, 'Your message was sent.')
            else:
                messages.error(request, 'Email or Phone is Invalid!')
    return render(request, 'contact.html', {})


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
    results = Blog.objects.none()

    if query:
        query_list = query.split()
        for word in query_list:
            results = results | Blog.objects.filter(
                Q(title__icontains=word) | Q(content__icontains=word)
            ).order_by('-time')

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
