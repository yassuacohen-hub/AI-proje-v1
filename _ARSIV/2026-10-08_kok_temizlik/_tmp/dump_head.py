import gzip
with gzip.open("backups/supabase_20261010_122308.sql.gz", "rt", encoding="utf-8", errors="replace") as f:
    for i in range(50):
        print(repr(next(f)))
