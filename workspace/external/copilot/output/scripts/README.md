# Operasyon Scriptleri Kullanım Rehberi

Bu klasörde, Ankara B2B Company Master projesi için operasyonel yardımcı Python scriptleri bulacaksınız.

> PowerShell uyumluluğu: Tüm scriptler `.sh` dosyaları yerine `.py` ile çalıştırılır. PowerShell'de bash escaping sorunları yaşamadan doğrudan `python scripts/backup_db.py` komutuyla çalıştırın.

## Scriptler

### backup_db.py
- Amaç: PostgreSQL veritabanı yedeklemesi (custom format -Fc)
- Kullanım: `python scripts/backup_db.py`
- Ortam değişkenleri: `DATABASE_URL`
- Çıktı: `backups/backup_TIMESTAMP.dump`
- Rotasyon: 7 günlük, 4 haftalık, 6 aylık
- Log: `logs/backup_db.log`

### healthcheck.py
- Amaç: Sistem ve uygulama sağlık kontrolü
- Kullanım: `python scripts/healthcheck.py`
- Ortam değişkenleri: `DATABASE_URL`, `HEALTHCHECK_API_URL`, `HEALTHCHECK_OUTPUT`
- Çıktı: JSON formatında sağlık raporu
- Exit code: `0=OK`, `1=degraded`, `2=critical`
- Log: `logs/healthcheck.log`

## Ortam Değişkenleri

| Değişken | Açıklama | Zorunlu |
|----------|----------|--------|
| DATABASE_URL | PostgreSQL bağlantı dizgesi | Hayır |
| HEALTHCHECK_API_URL | Sağlık kontrolü API endpoint | Hayır |
| HEALTHCHECK_OUTPUT | JSON çıktı dosyası yolu | Hayır |

## Kurulum

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install sqlalchemy requests psutil

    $env:DATABASE_URL="postgresql://user:pass@host:5432/db"
    python scripts\backup_db.py
    python scripts\healthcheck.py

## Notlar

- `.env` dosyasından da ortam değişkenleri okunabilir.
- Hata durumunda ilgili `logs/` altına yazılır.
- `backup_db.py` için sisteminizde `pg_dump` kurulu olmalıdır (`winget install PostgreSQL.PostgreSQL.17`).

