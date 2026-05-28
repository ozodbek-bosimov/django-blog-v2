# Django Blog (O'zbekcha)

Shaxsiy blog va portfolio sayti. Django + Tailwind + CKEditor 5 asosida yozilgan. Ushbu loyiha zamonaviy qulayliklar va xavfsizlik funksiyalari bilan to'liq jihozlangan.

## Asosiy imkoniyatlar
- **Blog, Kategoriya va Portfolio:** Postlar, ish tajribalari (Experiences), loyihalar (Projects) va ko'nikmalar (Skills).
- **Admin Panel & Rich Text:** To'liq kontent boshqaruvi va CKEditor 5 orqali qulay tahrirlash.
- **Shared Files Manager (Yangi):** Har xil turdagi fayllarni (PDF, HTML, Audio) yuklash, ulashish va Admin paneldan nusxalash (Copy URL).
- **Avtomatik WebP siqish:** Rasmlar sifatni yo'qotmagan holda WebP formatiga o'tkazilib disk hajmini va trafikni tejaydi.
- **Tezkor Kesh (Caching):** Sayt maksimal tezlikda ishlashi uchun sahifalar xotirada saqlanadi.
- **Rate Limiting (Himoya):** Kiberhujumlar va sun'iy trafik (DDOS) dan saqlanish uchun avtomatik himoya va bloklash tizimi.
- **Static/media servis:** WhiteNoise + Nginx integratsiyasi.

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
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
ADMIN_SESSION_TIMEOUT=1800
ADMIN_LOG_RETENTION_ENABLED=true
ADMIN_LOG_RETENTION_DAYS=90
DJANGO_FILE_LOGGING=false
GLOBAL_RATE_LIMIT_EXEMPT_PATH_PREFIXES=/_owner/,/static/,/media/,/shared/
```

### 3) Migratsiya va run
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Production `.env` namunasi (Server uchun)
Serverga joylash uchun hozirlangan `.env.deploy` faylidan foydalaning (Nusxa oling: `cp .env.deploy .env`):
```env
DJANGO_SECRET_KEY=your-long-random-secret
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=ozodbek.me,www.ozodbek.me
DJANGO_CSRF_TRUSTED_ORIGINS=https://ozodbek.me,https://www.ozodbek.me

# Xavfsizlik (Productionda YOQILGAN bo'lishi shart)
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SECURE_HSTS_SECONDS=31536000

# Himoya tizimi (DDOS va blokerlar)
GLOBAL_RATE_LIMIT_ENABLED=true
GLOBAL_RATE_LIMIT_EXEMPT_PATH_PREFIXES=/_owner/,/static/,/media/,/shared/
```

> Eslatma: `DJANGO_FILE_LOGGING=true` qilsangiz, `logs/` papkasiga yozish ruxsati bo‘lishi shart.

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

    client_max_body_size 20m;

    location /static/ {
        alias /var/www/django-blog/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/django-blog/media/;
        expires 7d;
    }

    # Yangi: Shared files xavfsiz va tez ishlashi uchun
    location /shared/ {
        alias /var/www/django-blog/shared/;
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

---

## Ko‘p uchraydigan xatolar va yechimlar

### 1) Admin login POST’da 500 yoki Rasm/Shared fayl yuklanmayapti
**Sabablar:** Baza (`db.sqlite3`) yoki maxsus papkalarga (`media`, `shared`, `logs`) yozish ruxsati yo‘q.
**Yechim:**
```bash
sudo chown www-data:www-data /var/www/django-blog/db.sqlite3
sudo chmod 664 /var/www/django-blog/db.sqlite3
sudo mkdir -p /var/www/django-blog/shared
sudo chown -R www-data:www-data /var/www/django-blog/logs /var/www/django-blog/media /var/www/django-blog/shared
sudo chmod -R u+rwX,g+rwX /var/www/django-blog/logs /var/www/django-blog/media /var/www/django-blog/shared
sudo systemctl restart gunicorn
```

### 2) Rasm yoki Fayl yuklashda 413/403 xato (Nginx)
**Sabab:** Nginx da katta fayllarni uzatish ruxsat etilmagan (standart 1MB turadi).
**Yechim:** Nginx konfiguratsiyasiga `client_max_body_size 20m;` qatorini qo'shing va `sudo systemctl reload nginx` qiling.

### 3) IP Bloklanishi (Rate Limit) Admin yoki Static sahifalarda ko'p uchrayapti
**Sabab:** Kesh va Statik ruxsatnomalar eski versiyada turibdi yoki fayllar bloklangan.
**Yechim:** `.env` faylda `GLOBAL_RATE_LIMIT_EXEMPT_PATH_PREFIXES=/_owner/,/static/,/media/,/shared/` ekanligini ta'minlang.

---

## Foydali buyruqlar
```bash
python manage.py check --deploy  # Xavfsizlik bo'yicha to'liq tekshirish
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl status gunicorn --no-pager -l
sudo journalctl -u gunicorn -n 120 --no-pager
sudo tail -n 120 /var/log/nginx/error.log
```
