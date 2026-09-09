"""Probe v2: DATABASE_URL'i doğrudan kullan."""
import os
from pathlib import Path
import traceback

# .env yükle
env_path = Path(r"C:\Projeler\Huginn Data Insights\.env")
for line in env_path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ[k] = v.strip().strip('"').strip("'")

url = os.environ.get("DATABASE_URL", "")
print(f"URL var: {bool(url)}")
if not url:
    print("HATA: DATABASE_URL yok")
    raise SystemExit(1)

print(f"URL sema: {url.split('://')[0]}")
print(f"URL host (kısmi): {url.split('@')[-1][:60]}")

try:
    import psycopg
    print(f"psycopg sürümü: {psycopg.__version__ if hasattr(psycopg,'__version__') else 'n/a'}")
    conn = psycopg.connect(url, connect_timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT version()")
    row = cur.fetchone()
    print(f"Bağlantı OK: {row[0][:60] if row else 'boş'}")
    conn.close()
    print("SUCCESS")
except Exception as e:
    print("HATA:", str(e)[:300])
    traceback.print_exc()
