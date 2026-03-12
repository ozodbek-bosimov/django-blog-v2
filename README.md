# Django Blog (O'zbekcha)

Shaxsiy blog va portfolio sayti. Django + Tailwind + CKEditor 5 asosida yozilgan.

## Asosiy imkoniyatlar
- Blog postlar, kategoriya va qidiruv
- Admin panel orqali kontent boshqaruvi
- Rich text editor (CKEditor 5)
- Static/media servis (WhiteNoise + Nginx)

## Texnologiyalar
- Django 5.x
- SQLite (hozirgi konfiguratsiya)
- Gunicorn + Nginx
- WhiteNoise
- django-tailwind
- django-ckeditor-5

---

## Lokal ishga tushirish

### 1) Muhit va paketlar
```bash
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2) `.env` yarating
```env
DJANGO_SECRET_KEY=your-local-secret
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=
ADMIN_SESSION_TIMEOUT=1800
ADMIN_LOG_RETENTION_ENABLED=true
ADMIN_LOG_RETENTION_DAYS=90
DJANGO_FILE_LOGGING=false
```

### 3) Migratsiya va run
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Production `.env` namunasi
```env
DJANGO_SECRET_KEY=your-long-random-secret
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=ozodbek.me,www.ozodbek.me
DJANGO_CSRF_TRUSTED_ORIGINS=https://ozodbek.me,https://www.ozodbek.me

ADMIN_SESSION_TIMEOUT=1800
ADMIN_LOG_RETENTION_ENABLED=true
ADMIN_LOG_RETENTION_DAYS=90

DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_SECURE_SSL_REDIRECT=true

DJANGO_FILE_LOGGING=false
```

> Eslatma: `DJANGO_FILE_LOGGING=true` qilsangiz, `logs/` papkasiga yozish ruxsati bo‘lishi shart.

---

## Muhim sozlamalar (hozirgi holat)

### Static (Django 5 mos)
Loyihada production uchun `STORAGES` ishlatiladi:
- `default` -> `django.core.files.storage.FileSystemStorage`
- `staticfiles` -> `whitenoise.storage.CompressedManifestStaticFilesStorage`

Bu `STATICFILES_STORAGE` o‘rniga Django 5 uchun to‘g‘ri yo‘l.

### Logging fallback
`DJANGO_FILE_LOGGING=true` bo‘lsa ham, `logs/` yoziladigan bo‘lmasa servis yiqilib ketmasligi uchun himoya qo‘shilgan.

---

## Gunicorn (systemd) tavsiya qilingan servis

`/etc/systemd/system/gunicorn.service`

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

Faollashtirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn --no-pager -l
```

---

## Nginx konfiguratsiya (asosiy)

`/etc/nginx/sites-available/django-blog`

```nginx
upstream gunicorn {
    server unix:/run/gunicorn/gunicorn.sock fail_timeout=0;
}

server {
    server_name ozodbek.me www.ozodbek.me;

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
    # ssl_certificate ...
    # ssl_certificate_key ...
}

server {
    listen 80;
    server_name ozodbek.me www.ozodbek.me;
    return 301 https://$host$request_uri;
}
```

Tekshiruv:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Deploy checklist (copy-paste)

```bash
cd /var/www/django-blog && \
git pull && \
source env/bin/activate && \
pip install -r requirements.txt && \
python manage.py migrate && \
python manage.py collectstatic --clear --noinput && \
sudo systemctl restart gunicorn && \
sudo systemctl reload nginx
```

Deploydan keyin health-check:
```bash
curl -I https://ozodbek.me/
curl -I https://ozodbek.me/admin/login/
curl -I https://ozodbek.me/static/favicon/favicon.ico
```

---

## Holatlar (Status Playbook)

### 1) `Healthy`
Belgilar:
- `curl -I https://ozodbek.me/` -> `200`
- `curl -I https://ozodbek.me/admin/login/` -> `200`
- `gunicorn` active

Tekshiruv:
```bash
sudo systemctl status gunicorn --no-pager -l
sudo nginx -t
```

### 2) `Degraded`
Belgilar:
- Ba’zan `500`, ba’zan normal ishlash
- Restart paytida qisqa uzilishlar

Diagnostika:
```bash
sudo journalctl -u gunicorn -f --no-pager
sudo tail -f /var/log/nginx/error.log
```

### 3) `Down` (502)
Belgilar:
- `HTTP/1.1 502 Bad Gateway`

Tezkor tiklash:
```bash
sudo systemctl stop gunicorn
sudo rm -f /run/gunicorn/gunicorn.sock
sudo systemctl start gunicorn
sudo systemctl restart nginx
```

---

## Ko‘p uchraydigan xatolar va yechimlar

### A) Favicon chiqmayapti
Sabablar:
- `collectstatic` qilinmagan
- `/static/favicon/*` hali eski cache

Yechim:
```bash
python manage.py collectstatic --clear --noinput
curl -I https://ozodbek.me/static/favicon/favicon.ico
```

### B) Admin login POST’da 500
Sabablar:
- DB yoki papkalarga yozish ruxsati yo‘q

Yechim:
```bash
sudo chown www-data:www-data /var/www/django-blog/db.sqlite3
sudo chmod 664 /var/www/django-blog/db.sqlite3
sudo chown -R www-data:www-data /var/www/django-blog/logs /var/www/django-blog/media
sudo chmod -R u+rwX,g+rwX /var/www/django-blog/logs /var/www/django-blog/media
sudo systemctl restart gunicorn
```

### C) `Unable to configure handler 'file'`
Sabab:
- `DJANGO_FILE_LOGGING=true` + `logs/` yozilmaydi

Yechim:
```bash
# variant 1
DJANGO_FILE_LOGGING=false

# variant 2
sudo mkdir -p /var/www/django-blog/logs
sudo chown -R www-data:www-data /var/www/django-blog/logs
```

---

## Foydali buyruqlar
```bash
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl status gunicorn --no-pager -l
sudo journalctl -u gunicorn -n 120 --no-pager
sudo tail -n 120 /var/log/nginx/error.log
```

---

## Xavfsizlik eslatmasi
- `DJANGO_DEBUG=false` productionda majburiy
- `.env` ni gitga push qilmang
- SQLite production uchun cheklangan; katta trafikda PostgreSQL tavsiya qilinadi
