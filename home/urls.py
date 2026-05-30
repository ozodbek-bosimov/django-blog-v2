from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("blog/", views.blog, name="blog"),
    path("projects/", views.projects, name="projects"),
    path("blog/<str:slug>/", views.blogpost, name="blogpost"),
    path("category/<str:category>/", views.category, name="category"),
    path("categories/", views.categories, name="categories"),
    path("search/", views.search, name="search"),
]
