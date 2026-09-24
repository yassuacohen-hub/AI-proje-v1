import os
from pathlib import Path

from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]


def load_urls() -> list[str]:
    urls = []
    if os.environ.get("DATABASE_URL"):
        urls.append(os.environ["DATABASE_URL"])
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL") and "=" in line:
                u = line.split("=", 1)[1].strip().strip('"').strip("'")
                if u and u not in urls:
                    urls.append(u)
    return urls


if __name__ == "__main__":
    urls = load_urls()
    for url in urls:
        try:
            eng = create_engine(url)
            with eng.begin() as conn:
                conn.execute(text("DELETE FROM credit_ledger WHERE user_id IN "
                                  "(SELECT user_id FROM users WHERE email LIKE 'testuye%')"))
                conn.execute(text("DELETE FROM users WHERE email LIKE 'testuye%'"))
            print(f"OK: {url.split('@')[-1][:60]}")
        except Exception as e:
            print(f"SKIP: {e}")
