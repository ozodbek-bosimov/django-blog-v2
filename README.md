# Django Blog & Portfolio (O'zbekcha)

Shaxsiy blog va portfolio sayti. Django, Tailwind CSS va CKEditor 5 asosida yaratilgan. Ushbu loyiha zamonaviy dizayn, qulay boshqaruv tizimi, yuqori xavfsizlik va optimal ishlash tezligi (performance) kabi xususiyatlarni o'z ichiga oladi.

## 🚀 Asosiy Imkoniyatlar

- **Blog Tizimi**: Maqolalar yozish, kategoriyalar bo'yicha ajratish (topics), o'qish vaqtini avtomatik hisoblash (reading time) va YouTube videolarini xavfsiz formatda (sanitized iframe) joylashtirish.
- **Portfolio & Tajriba**: Loyihalar (Projects), ish tajribasi (Experience & Roles, timeline formatida) hamda ko'nikmalar (Skills) sahifalari. Barcha ma'lumotlar Admin paneldan to'liq boshqariladi.
- **About Me (Singleton)**: Bosh sahifadagi shaxsiy ma'lumotlar, ijtimoiy tarmoq linklari va rezyumeni (CV) boshqarish tizimi. Faqat bitta (yagona) ob'yekt sifatida saqlanadi.
- **Admin Panel & Rich Text**: CKEditor 5 orqali maqola va bio matnlarini chiroyli yozish, formatlash va rasm/videolarni to'g'ridan-to'g'ri matn ichiga joylash.
- **Fayllar Boshqaruvi (Shared Files)**: Katta hajmli fayllarni yuklash, ro'yxatini ko'rish, Admin paneldan turib URL-dan bevosita nusxa olish (Copy URL) va `/shared/` linki orqali ulashish.
- **Avtomatik Kesh (Caching)**: Sayt sahifalari va ma'lumotlar (LocMemCache yordamida) xotirada saqlanadi. Model o'zgarganda (Signallar yordamida) kesh avtomatik tozalanadi.
- **Avtomatik WebP va Siqish**: Rasm yuklanganda sifati saqlab qolingan holda hajmi kichraytiriladi va avtomatik ravishda WebP formatiga o'tkaziladi.
- **Avto-tozalash tizimi (Cleanup Signals)**: Maqola yoki biror ob'yekt tahrirlanganda yoki o'chirilganda, u bilan bog'liq eski rasmlar, CKEditor ichidagi ishlatilmayotgan media fayllar diskdan o'zi tozalanadi.
- **Rate Limiting & Xavfsizlik**: IP orqali so'rovlar sonini cheklash (DDOS va botlarga qarshi middleware). CSRF, XSS va boshqa hujumlarga qarshi xavfsizlik choralari.
- **Admin Session & Log Pruning**: Admin seanslari xavfsizligini ta'minlash maqsadida belgilangan vaqt (Timeout) sozlamasi va Admin panel harakatlari tarixini (LogEntry) eski yozuvlardan avtomatik/qo'lda tozalash.

## 🛠 Texnologiyalar

- **Backend:** Django 5.x
- **Baza (Database):** SQLite (Standart konfiguratsiya, ko'chirish oson)
- **Frontend:** Django Templates, Tailwind CSS
- **Matn Muharriri:** django-ckeditor-5
- **Server / Deploy:** Gunicorn, Nginx, WhiteNoise (static fayllar uchun)
- **Rasm Bilan Ishlash:** Pillow (WebP siqish va o'lchamlarini moslash)

---

## 💻 Lokal Muhitda Ishga Tushirish (Development)

### 1. Loyihani yuklab olish va paketlarni o'rnatish
```bash
git clone <repo-url>
cd django-blog-v2
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. `.env` faylini yaratish
Loyiha papkasida `.env` fayl yarating va quyidagilarni kiriting:
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

### 3. Migratsiya va serverni yurgizish
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

*(Tailwind CSS o'zgarishlarini kuzatish uchun alohida terminal oynasida: `python manage.py tailwind start` yozishingiz mumkin)*

---

## 🌍 Serverga Joylash (Production Deployment)

### 1. Muhit O'zgaruvchilari (Environment Variables)
Production muhiti uchun loyihadagi `.env.deploy` nusxasidan foydalaning:
```bash
cp .env.deploy .env
```
Fayl ichidagi o'zgaruvchilarni serveringiz (domen nomlari) ga qarab to'g'rilab chiqing. Xavfsizlik va Rate Limit (Himoya) sozlamalari odatda yoqiq bo'lishi kerak.

### 2. Gunicorn (systemd) xizmatini sozlash
Tavsiya etiladigan `/etc/systemd/system/gunicorn.service` fayli:

```ini
[Unit]
Description=gunicorn daemon for django-blog
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/django-blog-v2
Environment="PATH=/var/www/django-blog-v2/env/bin"
Environment="DJANGO_ENV_FILE=.env"
ExecStart=/var/www/django-blog-v2/env/bin/gunicorn --workers 1 --bind unix:/run/gunicorn/gunicorn.sock blogApp.wsgi:application
RuntimeDirectory=gunicorn
RuntimeDirectoryMode=0755
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
Servisni faollashtirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

### 3. Nginx Konfiguratsiyasi (Asosiy ko'rinish)
`/etc/nginx/sites-available/django-blog`

```nginx
upstream gunicorn {
    server unix:/run/gunicorn/gunicorn.sock fail_timeout=0;
}

server {
    server_name ozodbek.me www.ozodbek.me;
    client_max_body_size 20m;

    location /static/ {
        alias /var/www/django-blog-v2/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/django-blog-v2/media/;
        expires 7d;
    }

    location /shared/ {
        alias /var/www/django-blog-v2/shared/;
        expires 30d;
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
    # ssl_certificate /path/to/fullchain.pem;
    # ssl_certificate_key /path/to/privkey.pem;
}

server {
    listen 80;
    server_name ozodbek.me www.ozodbek.me;
    return 301 https://$host$request_uri;
}
```
O'zgarishlarni kiritgach tekshirish: `sudo nginx -t && sudo systemctl reload nginx`

---

## 🚀 Deploy Checklist (Copy-Paste)

Yangi o'zgarishlarni serverga tortish va ishga tushirish uchun qisqa buyruq:
```bash
cd /var/www/django-blog-v2 && \
git pull && \
source env/bin/activate && \
pip install -r requirements.txt && \
python manage.py migrate && \
python manage.py collectstatic --clear --noinput && \
sudo systemctl restart gunicorn && \
sudo systemctl reload nginx
```

---

## 💡 Foydali Buyruqlar

```bash
python manage.py check --deploy  # Xavfsizlik bo'yicha to'liq tekshirish
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl status gunicorn --no-pager -l
sudo journalctl -u gunicorn -n 120 --no-pager
sudo tail -n 120 /var/log/nginx/error.log
```

---

## 🎨 Kod Uslubi (Formatting & Linting)

Loyiha bo'ylab kod uslubi bir xil bo'lishi uchun quyidagi qoidalar amal qiladi:

- **Python** — `ruff` (`pyproject.toml` da sozlangan): 4 bo'shliq, ikki tirnoq (`"`).
- **JS / CSS / HTML** — 2 bo'shliq (`.editorconfig` da belgilangan).
- Avtomatik yaratiladigan fayllar (`migrations/`, `staticfiles/`, `static/css/dist/`) formatlanmaydi.

```bash
# Python kodni formatlash va tekshirish
env/bin/ruff format .          # kodni avtomatik formatlash
env/bin/ruff check . --fix     # import tartibi va boshqa xatolarni tuzatish
env/bin/ruff check .           # faqat tekshirish (CI uchun)

# Testlar
python manage.py test home
```

> Eslatma: `.editorconfig` faylini qo'llab-quvvatlovchi muharrirlar (VS Code,
> PyCharm) bo'shliq/indent qoidalarini avtomatik qo'llaydi.

---

## 🛠 Ko‘p Uchraydigan Xatolar va Ularning Yechimi

1. **Rasm yoki Fayl yuklashda "Server Error (500)" yoxud sahifada rasm ishlamay qolishi:**
   `media`, `shared`, jurnallar papkasi `logs` va `db.sqlite3` fayllariga Nginx/Gunicorn foydalanuvchisi (`www-data`) yozish ruxsatiga ega bo'lishi shart.
   ```bash
   sudo chown -R www-data:www-data /var/www/django-blog-v2/media /var/www/django-blog-v2/shared /var/www/django-blog-v2/logs
   sudo chown www-data:www-data /var/www/django-blog-v2/db.sqlite3
   sudo chmod -R 775 /var/www/django-blog-v2/media /var/www/django-blog-v2/shared
   sudo chmod 664 /var/www/django-blog-v2/db.sqlite3
   ```
2. **Katta fayl (Masalan `SharedFiles` orqali) yuklayotganda "413 Request Entity Too Large":**
   Nginx konfiguratsiyasidagi `client_max_body_size` qiymati Django limitidan (`DATA_UPLOAD_MAX_MEMORY_SIZE`) kichik bo'lmasligi kerak (masalan `20m;`). Qo'shgach Nginx-ni qayta ishga tushiring.
3. **Sahifalar tez-tez kirilganda "429 Too Many Requests" (IP bloklanishi):**
   Saytdagi DDOS va agressiv botlarga qarshi Rate Limit himoyasi ishlab ketdi. `.env` dagi `GLOBAL_RATE_LIMIT_ENABLED` va tegishli sozlamalarni ko'rib chiqing. Statik fayllar (rasm, dizaynlar) bloklanmasligi uchun `GLOBAL_RATE_LIMIT_EXEMPT_PATH_PREFIXES` ichida `/static/,/media/,/shared/` kabilar albatta kiritilganligini tekshiring.
