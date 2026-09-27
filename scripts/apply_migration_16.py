import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as c:
    c.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ NULL"))
    c.execute(text("CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login)"))
    c.commit()
    print("Migration applied")

# Verify
with eng.connect() as c:
    cols = c.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'last_login'")).fetchall()
    print("last_login column:", cols)
    idx = c.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'users' AND indexname = 'idx_users_last_login'")).fetchall()
    print("index:", idx)
