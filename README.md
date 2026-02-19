# Django Blog (O'zbekcha)

## Loyihaning qisqacha tavsifi
Bu loyiha Django asosida yozilgan shaxsiy blog saytidir. Saytda postlar, kategoriyalar, qidiruv, hamda admin panel orqali kontent boshqaruvi mavjud. Statik fayllar va media fayllar bilan ishlash sozlangan.

## Texnologiyalar
- Django
- SQLite (lokal)
- Whitenoise (static serve)
- Tailwind (django-tailwind)
- TinyMCE (tahrirlash)

## Lokal ishga tushirish
1. Virtual environment yarating va yoqing.
2. Kutubxonalarni o'rnating:

```bash
pip install -r requirements.txt
```

3. .env faylni tekshiring (lokal uchun):

```env
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

4. Migratsiyalarni ishga tushiring:

```bash
python manage.py migrate
```

5. Admin uchun superuser yarating:

```bash
python manage.py createsuperuser
```

6. Serverni ishga tushiring:

```bash
python manage.py runserver
```

## Muhim sozlamalar (.env)
- DJANGO_SECRET_KEY: xavfsizlik uchun maxfiy kalit.
- DJANGO_DEBUG: lokalda true, serverda false.
- DJANGO_ALLOWED_HOSTS: domenlar ro'yxati (vergul bilan).
- DJANGO_CSRF_TRUSTED_ORIGINS: https bilan to'liq domenlar.
- ADMIN_SESSION_TIMEOUT: admin sessiya muddati (sekund).

## Static va Media
- Static fayllar productionda collectstatic orqali yig'iladi.
- Media fayllar (rasmlar) MEDIA_ROOT ichida saqlanadi.

## Deploy (Production)

### 1. Server tayyorlash
```bash
# Loyihani clone qiling
git clone --depth 1 git@github.com:ozodbek-bosimov/django-blog.git
cd django-blog

# Virtual environment yarating
python3 -m venv env
source env/bin/activate

# Paketlarni o'rnating
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Production .env yarating
`.env.example` dan nusxa olib, production qiymatlarini yozing:
```bash
cp .env.example .env
nano .env
```

**Production `.env` misoli:**
```env
DJANGO_SECRET_KEY=your-real-long-random-secret-key-here-64-chars
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
ADMIN_SESSION_TIMEOUT=1800
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_SECURE_SSL_REDIRECT=true
```

**Secret key generatsiya:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Database migratsiyalar
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Gunicorn service (systemd)
`/etc/systemd/system/gunicorn.service` yarating:
```ini
[Unit]
Description=gunicorn daemon for django-blog
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/django-blog
Environment="PATH=/var/www/django-blog/env/bin"
ExecStart=/var/www/django-blog/env/bin/gunicorn --workers 2 --bind unix:/run/gunicorn/gunicorn.sock blogApp.wsgi:application
RuntimeDirectory=gunicorn
RuntimeDirectoryMode=0755
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Faollashtiring:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

### 5. Nginx konfiguratsiya
`/etc/nginx/sites-available/django-blog` yarating:
```nginx
upstream gunicorn {
    server unix:/run/gunicorn/gunicorn.sock fail_timeout=0;
}

server {
    server_name your-domain.com www.your-domain.com;

    location /static/ {
        alias /var/www/django-blog/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/django-blog/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$host$request_uri;
}
```

Faollashtiring:
```bash
sudo ln -s /etc/nginx/sites-available/django-blog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 7. Update qilish
```bash
cd /var/www/django-blog
git pull
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

## Muhim eslatmalar
- Production da `DJANGO_DEBUG=false` bo'lishi SHART
- `.env` faylni hech qachon Git ga push qilmang
- `db.sqlite3` production uchun yaxshi emas — PostgreSQL/MySQL ishlatish tavsiya
- Static fayllar `collectstatic` orqali yig'ilishi kerak

## Admin sessiya timeout
Admin panelda ishlaganda sessiya vaqtini ADMIN_SESSION_TIMEOUT orqali boshqarasiz (sekund). Har bir admin so'rovda sessiya yangilanadi.

## Foydali buyruqlar
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```
