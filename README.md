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

## Deploy (Alwaysdata uchun qisqa yo'l)
1. Kodni serverga yuklang (git yoki scp bilan).
2. Virtual environment yarating va faollashtiring.
3. Kutubxonalarni o'rnating:

```bash
pip install -r requirements.txt
```

4. Server uchun .env yarating:

```env
DJANGO_SECRET_KEY=real-secret
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
ADMIN_SESSION_TIMEOUT=1800
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_SECURE_SSL_REDIRECT=true
```

5. Migratsiyalarni ishga tushiring:

```bash
python manage.py migrate
```

6. Static fayllarni yig'ing:

```bash
python manage.py collectstatic
```

7. Alwaysdata boshqaruv panelida WSGI/Gunicorn sozlang:

```bash
gunicorn blogApp.wsgi
```

## Admin sessiya timeout
Admin panelda ishlaganda sessiya vaqtini ADMIN_SESSION_TIMEOUT orqali boshqarasiz (sekund). Har bir admin so'rovda sessiya yangilanadi.

## Foydali buyruqlar
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```
