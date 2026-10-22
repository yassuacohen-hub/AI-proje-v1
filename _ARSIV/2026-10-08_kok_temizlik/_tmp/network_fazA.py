import os
import psycopg2

# Supabase DATABASE_URL from .env
DATABASE_URL = "postgresql://postgres.kypoqtgbrxknyazwlhxq:GXFRIEn0cd4JxIIn@aws-0-eu-west-2.pooler.supabase.com:6543/postgres"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=== entity_graph şeması ===")
cur.execute("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'entity_graph'
ORDER BY ordinal_position
""")
for r in cur.fetchall():
    print(r)

cur.execute("SELECT count(*) FROM entity_graph")
print("Satır sayısı:", cur.fetchone()[0])

cur.execute("""
SELECT count(*) FROM entity_graph eg
JOIN company_persons cp ON cp.vkn = eg.target_vkn OR cp.vkn = eg.source_vkn
""")
print("company_persons bağlantılı satır:", cur.fetchone()[0])

print("=== Derinlik 2'de en kalabalık 5 firma ===")
cur.execute("""
WITH RECURSIVE cte AS (
  SELECT source_vkn, target_vkn, 1 as derinlik, source_vkn as kok
  FROM entity_graph
  UNION ALL
  SELECT cte.kok, eg.target_vkn, cte.derinlik + 1, cte.kok
  FROM cte
  JOIN entity_graph eg ON eg.source_vkn = cte.target_vkn
  WHERE cte.derinlik < 2
)
SELECT kok, count(DISTINCT target_vkn) as dugum_sayisi
FROM cte
GROUP BY kok
ORDER BY dugum_sayisi DESC
LIMIT 5
""")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()