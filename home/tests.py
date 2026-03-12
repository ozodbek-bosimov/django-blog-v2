from __future__ import annotations

from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from home.context_processors import USED_TAGS_CACHE_KEY, used_tags
from home.models import AboutMe, Blog
from home.templatetags.blog_extras import reading_time


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests",
        }
    }
)
class BlogModelTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_blog_effective_thumbnail_prefers_upload(self):
        blog = Blog.objects.create(
            title="t",
            meta="m",
            content="c",
            thumbnail_url="https://example.com/x.jpg",
            category="Test",
            slug="s1",
        )

        self.assertEqual(blog.effective_thumbnail, "https://example.com/x.jpg")

        class _FakeFieldFile:
            url = "/media/images/upload.jpg"

        blog.thumbnail_img = _FakeFieldFile()
        self.assertEqual(blog.effective_thumbnail, "/media/images/upload.jpg")

    def test_blog_save_normalizes_category_and_clears_cache(self):
        cache.set(USED_TAGS_CACHE_KEY, ["cached"])
        blog = Blog.objects.create(
            title="t",
            meta="m",
            content="c",
            category="  PyThOn  ",
            slug="s2",
        )
        blog.refresh_from_db()
        self.assertEqual(blog.category, "python")
        self.assertIsNone(cache.get(USED_TAGS_CACHE_KEY))


class AboutMeSingletonTests(TestCase):
    def test_aboutme_second_save_updates_existing_instead_of_creating(self):
        first = AboutMe.objects.create(
            name="A",
            profession="P",
            bio="B",
            email="a@example.com",
        )
        self.assertEqual(AboutMe.objects.count(), 1)

        second = AboutMe(
            name="A2",
            profession="P2",
            bio="B2",
            email="a2@example.com",
        )
        second.save()

        self.assertEqual(AboutMe.objects.count(), 1)
        only = AboutMe.objects.get()
        self.assertEqual(only.pk, first.pk)
        self.assertEqual(only.name, "A2")


class TemplateTagTests(TestCase):
    def test_reading_time_min_1(self):
        self.assertEqual(reading_time(""), 1)
        self.assertEqual(reading_time(None), 1)
        self.assertEqual(reading_time("<p>Hello</p>"), 1)

    def test_reading_time_ceil_160_wpm(self):
        # 161 words => ceil(161/160) = 2 minutes
        content = " ".join(["word"] * 161)
        self.assertEqual(reading_time(content), 2)

    def test_reading_time_strips_html(self):
        # Should count words, not tags/attrs
        content = '<p>Hello <a href="x">world</a></p>'
        self.assertEqual(reading_time(content), 1)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests",
        }
    }
)
class ContextProcessorTests(TestCase):
    def setUp(self):
        cache.clear()
        self.rf = RequestFactory()

    def test_used_tags_returns_distinct_sorted(self):
        Blog.objects.create(
            title="t1",
            meta="m",
            content="c",
            category="python",
            slug="c1",
        )
        Blog.objects.create(
            title="t2",
            meta="m",
            content="c",
            category="django",
            slug="c2",
        )
        Blog.objects.create(
            title="t3",
            meta="m",
            content="c",
            category="django",
            slug="c3",
        )
        data = used_tags(self.rf.get("/"))
        self.assertEqual(data["used_tags"], ["django", "python"])

    def test_used_tags_is_cached(self):
        Blog.objects.create(
            title="t1",
            meta="m",
            content="c",
            category="python",
            slug="c1",
        )
        _ = used_tags(self.rf.get("/"))
        self.assertEqual(cache.get(USED_TAGS_CACHE_KEY), ["python"])

        # Blog.save() clears the cache, so after creating a new blog
        # the cache should be invalidated and the next call returns fresh data.
        Blog.objects.create(
            title="t2",
            meta="m",
            content="c",
            category="django",
            slug="c2",
        )
        # Cache was cleared by Blog.save()
        self.assertIsNone(cache.get(USED_TAGS_CACHE_KEY))
        # Next call rebuilds cache with both tags
        data = used_tags(self.rf.get("/"))
        self.assertEqual(data["used_tags"], ["django", "python"])


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests",
        }
    }
)
class ViewsSmokeTests(TestCase):
    def setUp(self):
        cache.clear()

        self.blog = Blog.objects.create(
            title="Hello Django",
            meta="meta",
            content="<p>Some content</p>",
            category="django",
            slug="hello-django",
        )

    def test_home_page_ok(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "index.html")

    def test_blog_list_ok(self):
        resp = self.client.get(reverse("blog"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "blog.html")

    def test_blogpost_ok_and_context(self):
        resp = self.client.get(reverse("blogpost", kwargs={"slug": self.blog.slug}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "blogpost.html")
        self.assertIn("blog_url", resp.context)

    def test_blogpost_missing_returns_404_template(self):
        resp = self.client.get(reverse("blogpost", kwargs={"slug": "missing"}))
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, "404.html")

    def test_category_missing_shows_message(self):
        resp = self.client.get(reverse("category", kwargs={"category": "nope"}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "category.html")
        self.assertContains(resp, "No posts found in category")

    def test_search_empty_query_shows_message(self):
        resp = self.client.get(reverse("search"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "search.html")
        self.assertContains(resp, "Please enter a search query.")

    def test_search_finds_results(self):
        resp = self.client.get(reverse("search"), {"q": "Django"})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "search.html")
        self.assertIn("results", resp.context)
        self.assertTrue(resp.context["results"].paginator.count >= 1)

    def test_search_rate_limit_returns_429_and_flag(self):
        url = reverse("search")
        for _ in range(20):
            resp = self.client.get(url, {"q": "django"}, REMOTE_ADDR="1.2.3.4")
            self.assertEqual(resp.status_code, 200)

        resp = self.client.get(url, {"q": "django"}, REMOTE_ADDR="1.2.3.4")
        self.assertEqual(resp.status_code, 429)
        self.assertTrue(resp.context["rate_limited"])
