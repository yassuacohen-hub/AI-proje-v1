"""Geçici probe v4: pooler + SNI hostname."""
from pathlib import Path
from urllib.parse import quote
import psycopg

env_path = Path(__file__).resolve().parents[1] / ".env"
raw = [l.strip() for l in env_path.read_text().splitlines() if l.strip().startswith("postgresql://")][0]
pwd = raw.split("@")[0].split(":", 1)[1]
proj_ref = raw.split("@")[1].split(":")[0].split(".")[0]
sni = f"db.{proj_ref}.supabase.co"
pw = quote(pwd, safe="")

hosts = [
    "aws-0-eu-central-1.pooler.supabase.com",
    "aws-0-eu-west-1.pooler.supabase.com",
    "aws-0-eu-west-2.pooler.supabase.com",
]
for host in hosts:
    url = f"postgresql://postgres.{proj_ref}:{pw}@{host}:5432/postgres"
    try:
        conn = psycopg.connect(url, connect_timeout=6, sslsni=sni)
        print("OK", host, "->", conn.execute("select version()").fetchone()[0][:40])
        raise SystemExit(0)
    except Exception as e:
        print("FAIL", host, "::", str(e)[:200])