# Deployment Rehberi

> Versiyon: 1.0 | Güncelleme: 2026-09-14

## 1. Ortam Kurulumu

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-app.txt
```

## 2. Veritabani

### PostgreSQL (Uretim)
```bash
python -m src.company_master.schema.migrations.migrate --version
python -m src.company_master.schema.migrations.migrate --dry-run
```

### SQLite (Gelistirme)
.env'de DATABASE_URL=sqlite:///./test.db ayarla.

## 3. Redis

```bash
python -c "from src.company_master.cache.redis_cache import RedisCache; c=RedisCache(); c.set('t',1); print(c.get('t'))"
```

## 4. Calistirma

```bash
streamlit run app.py --server.port 8501
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

## 5. Mesaj Kuyrugu (BE-03)

```python
from src.company_master.queue.message_queue import RedisMessageQueue
q = RedisMessageQueue()
q.publish("t", {"d": 1})
m = q.consume("t")
print(m)
```

## 6. Sorun Giderme

| Sorun | Cozum |
|-------|-------|
| Redis hatasi | In-memory fallback devreye girer |
| DB hatasi | PostgreSQL servisini kontrol et |
| API key hatali | NINEROUTER_KEY .env'de dogrula |
| Migration hata | migrate.py --dry-run |

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
