# Django Blog & Portfolio

A personal blog and portfolio website built with **Django 6**, **Tailwind CSS**, **HTMX**, and **CKEditor 5**. Features a modern design, a convenient admin panel, robust security defaults, and optimized performance out of the box.

## Key Features

- **Blog System** — Write and publish articles, organize them by topics, auto-calculate reading time, and embed YouTube videos with sanitized iframes.
- **SPA-like Navigation** — Uses HTMX for seamless page transitions without full page reloads, providing a faster, app-like user experience.
- **Portfolio & Experience** — Showcase projects, work experience (displayed in a timeline format), and skills — all fully manageable from the admin panel.
- **About Me (Singleton)** — A single-instance model for managing personal info, social links, and a downloadable CV on the homepage.
- **Rich Text Editing** — CKEditor 5 integration for beautifully formatted articles and bio sections with inline images and videos.
- **Shared Files** — Upload large files, browse them, copy their public URL directly from the admin panel, and share via `/shared/` links.
- **Auto Caching** — Pages and querysets are cached in memory (LocMemCache). Caches are automatically invalidated through Django signals whenever a model changes.
- **Auto WebP & Compression** — Uploaded images are automatically compressed (preserving quality) and converted to WebP format.
- **Auto Cleanup (Signals)** — When an object is edited or deleted, its orphaned images and unused CKEditor media files are automatically removed from disk.
- **Rate Limiting & Security** — IP-based request throttling middleware to mitigate DDoS and bot abuse, plus built-in CSRF, XSS, and other attack protections.
- **Admin Session & Log Pruning** — Configurable admin session timeout and automatic (or manual) pruning of old admin action log entries.

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Backend** | Django 6.x |
| **Database** | SQLite (default — portable and easy to migrate) |
| **Frontend** | Django Templates, Tailwind CSS, HTMX |
| **Rich Text Editor** | django-ckeditor-5 |
| **Deployment** | Gunicorn, Nginx, WhiteNoise (static files) |
| **Image Processing** | Pillow (WebP conversion & resizing) |

---

## Local Development Setup

### 1. Clone the repository and install dependencies
```bash
git clone <repo-url>
cd personal-site
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Create the `.env` file
Create a `.env` file in the project root with the following contents:
```env
DJANGO_SECRET_KEY=your-local-secret-key
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
ADMIN_SESSION_TIMEOUT=1800
ADMIN_LOG_RETENTION_ENABLED=true
ADMIN_LOG_RETENTION_DAYS=90
DJANGO_FILE_LOGGING=false
GLOBAL_RATE_LIMIT_ENABLED=false
```

### 3. Run migrations and start the server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

> **Tip:** To watch Tailwind CSS changes in real time, open a separate terminal and run: `python manage.py tailwind start`

