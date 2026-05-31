from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("blog/", views.blog, name="blog"),
    path("projects/", views.projects, name="projects"),
    path("blog/<str:slug>/", views.blogpost, name="blogpost"),
    path("topic/<str:category>/", views.category, name="category"),
    path("topics/", views.categories, name="categories"),
    path("search/", views.search, name="search"),
    path("github-contributions/", views.github_calendar_proxy, name="github_contributions"),
    path("leetcode-proxy/", views.leetcode_proxy, name="leetcode_proxy"),
]
