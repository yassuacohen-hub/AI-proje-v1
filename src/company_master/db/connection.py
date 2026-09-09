"""Veritabanı bağlantı yardımcıları.



DATABASE_URL öncelik sırası:

    1. Ortam değişkeni DATABASE_URL

    2. .env dosyası (proje kökü)

    3. Fallback: sqlite:///./company_master.db (test için)

"""



import os

from functools import lru_cache

from pathlib import Path

from typing import Optional



def _find_root() -> Path:
    """Bu paketten proje kökünü (DATABASE_URL içeren .env) yukarı çıkar."""
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        env_path = candidate / ".env"
        if env_path.exists():
            try:
                if "DATABASE_URL" in env_path.read_text(encoding="utf-8"):
                    return candidate
            except Exception:
                pass
    # fallback: herhangi bir .env
    for candidate in [here, *here.parents]:
        if (candidate / ".env").exists():
            return candidate
    return here


def _load_env() -> None:
    """.env dosyasını yükler (python-dotenv yoksa kendi parser'ı)."""
    env_path = _find_root() / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


try:
    from dotenv import load_dotenv
    _r = _find_root()
    load_dotenv(_r / ".env")
except ImportError:
    _load_env()




try:

    from sqlalchemy import create_engine

    from sqlalchemy.engine import Engine

    from sqlalchemy.orm import Session, sessionmaker

    from sqlalchemy.pool import NullPool

    HAS_SQLALCHEMY = True

except ImportError:

    HAS_SQLALCHEMY = False




_FALLBACK_URL = "sqlite:///./company_master.db"




def get_database_url() -> str:

    """Aktif veritabanı URL'sini döndürür."""

    url = os.getenv("DATABASE_URL")

    if url:

        return url

    return _FALLBACK_URL
@lru_cache(maxsize=1)
def get_engine():
    """SQLAlchemy engine veya basit bağlantı."""
    if not HAS_SQLALCHEMY:
        import sqlite3
        url = get_database_url()
        if url.startswith("sqlite:///"):
            db_path = Path(url[len("sqlite:///"):])
        else:
            db_path = Path("./company_master.db")
        return sqlite3.connect(str(db_path))

    url = get_database_url()
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql"):
        return create_engine(
            url,
            echo=False,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            connect_args={"prepare_threshold": None, "options": "-c statement_timeout=0"},
        )
    return create_engine(url, echo=False, future=True)


def get_session():

    """Session nesnesi."""

    if not HAS_SQLALCHEMY:

        return None

    engine = get_engine()

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    return SessionLocal()




def init_db(sql_path: Optional[str] = None) -> None:

    """Şema SQL'ini çalıştırarak tabloları oluşturur.



    SQLite fallback modunda sadece temel companies tablosunu oluşturur.

    """

    if sql_path is None:

        sql_path = str(Path(__file__).resolve().parents[1] / "schema" / "companies.sql")



    url = get_database_url()

    if not HAS_SQLALCHEMY or url.startswith("sqlite"):

        # SQLite fallback: basit şema (PostgreSQL SQL'i SQLite'ta çalışmaz;

        # sqlalchemy kurulu olsa bile SQLite URL'si bu yola girer)

        import sqlite3

        db_path = url[len("sqlite:///"):] if url.startswith("sqlite:///") else "./company_master.db"

        conn = sqlite3.connect(str(db_path))

        cur = conn.cursor()

        cur.execute("""

        CREATE TABLE IF NOT EXISTS companies (

            company_id TEXT PRIMARY KEY,

            legal_name TEXT NOT NULL,

            trade_name TEXT,

            company_type TEXT,

            tax_number TEXT,

            mersis_number TEXT,

            establishment_date TEXT,

            status TEXT DEFAULT 'unknown',

            status_confidence REAL,

            employee_count INTEGER,

            website_domain TEXT,

            primary_phone TEXT,

            primary_email TEXT,

            description TEXT,

            data_quality_score REAL,

            entity_confidence REAL,

            is_ankara INTEGER DEFAULT 0,

            is_osb_member INTEGER DEFAULT 0,

            osb_id TEXT,

            nace_validity TEXT DEFAULT 'unknown',

            quarantine_reason TEXT,

            first_seen_at TEXT,

            last_verified_at TEXT,

            created_at TEXT,

            updated_at TEXT

        )""")

        cur.execute("""

        CREATE TABLE IF NOT EXISTS osbs (

            osb_id TEXT PRIMARY KEY,

            name TEXT NOT NULL,

            city TEXT NOT NULL,

            district TEXT,

            osb_type TEXT,

            status TEXT DEFAULT 'active',

            created_at TEXT

        )""")

        cur.execute("""

        CREATE TABLE IF NOT EXISTS quarantine_firms (

            quarantine_id TEXT PRIMARY KEY,

            raw_payload TEXT,

            error_reason TEXT,

            source_url TEXT,

            resolved_status INTEGER DEFAULT 0,

            created_at TEXT

        )""")

        conn.commit()

        conn.close()

        return

    

    # SQLAlchemy + raw SQL

    from sqlalchemy import text

    engine = get_engine()

    with open(sql_path, 'r', encoding='utf-8') as f:

        sql = f.read()

    with engine.begin() as conn:

        for statement in sql.split(';'):

            stmt = statement.strip()

            if stmt and not stmt.startswith('--'):

                try:

                    conn.execute(text(stmt))

                except Exception as e:

                    print(f"SQL hatası (atlanıyor): {e}")