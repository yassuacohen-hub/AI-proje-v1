from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with open('match_sql.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

print("SQL calistiriliyor...")
with engine.begin() as conn:
    # Her statement'i ayrı çalıştır (semicolon ile ayrılmış)
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
    for i, stmt in enumerate(statements):
        if stmt:
            try:
                result = conn.execute(text(stmt))
                if result.returns_rows:
                    rows = result.fetchall()
                    for row in rows:
                        print(f"  {row}")
                else:
                    print(f"  Statement {i+1}: OK (rowcount: {result.rowcount})")
            except Exception as e:
                print(f"  Statement {i+1} HATA: {e}")
                print(f"  SQL: {stmt[:100]}...")

print("\nTamamlandi!")