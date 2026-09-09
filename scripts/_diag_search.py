import sys, time, json
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

e = get_engine()
with e.connect() as c:
    # Check if search_text column exists
    cols = c.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='companies' AND column_name='search_text'")).fetchall()
    if not cols:
        print("Adding search_text computed column...")
        t0 = time.perf_counter()
        c.execute(text("""
            ALTER TABLE companies
            ADD COLUMN search_text TEXT GENERATED ALWAYS AS (
                COALESCE(legal_name, '') || ' ' ||
                COALESCE(trade_name, '') || ' ' ||
                COALESCE(primary_phone, '') || ' ' ||
                COALESCE(primary_email, '') || ' ' ||
                COALESCE(tax_number, '') || ' ' ||
                COALESCE(vergi_no, '')
            ) STORED
        """))
        c.commit()
        print(f"  Column added in {(time.perf_counter()-t0)*1000:.0f} ms")
    else:
        print("search_text column already exists")

    # Create GIN trigram index on search_text
    t0 = time.perf_counter()
    c.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_companies_search_text_trgm
        ON companies USING GIN (search_text gin_trgm_ops)
        WHERE is_ankara = TRUE AND is_osb_member = TRUE
    """))
    c.commit()
    print(f"  Index created in {(time.perf_counter()-t0)*1000:.0f} ms")

    # ANALYZE
    c.execute(text("ANALYZE companies"))
    c.commit()

    # Benchmark old query (multi-column ILIKE OR)
    old_sql = "SELECT c.legal_name FROM companies c WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE AND (c.legal_name ILIKE :s OR c.trade_name ILIKE :s OR c.primary_phone ILIKE :s OR c.primary_email ILIKE :s OR c.tax_number ILIKE :s OR c.vergi_no ILIKE :s) ORDER BY c.data_quality_score DESC LIMIT 50"
    
    # Benchmark new query (single column on computed search_text)
    new_sql = "SELECT c.legal_name FROM companies c WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE AND c.search_text ILIKE :s ORDER BY c.data_quality_score DESC LIMIT 50"
    
    for label, sql in [("OLD (multi-col ILIKE OR)", old_sql), ("NEW (search_text ILIKE)", new_sql)]:
        # EXPLAIN ANALYZE
        plan = c.execute(text("EXPLAIN (ANALYZE, FORMAT JSON) " + sql), {"s": "%dogan%"}).fetchone()
        plan_str = plan[0] if isinstance(plan[0], (list, dict)) else json.loads(plan[0])
        db_ms = plan_str[0]["Execution Time"]
        
        # Plain EXPLAIN
        expl = [r[0] for r in c.execute(text("EXPLAIN " + sql), {"s": "%dogan%"}).fetchall()]
        
        # Round-trip
        times = []
        for i in range(3):
            t0 = time.perf_counter()
            c.execute(text(sql), {"s": "%dogan%"}).fetchall()
            times.append((time.perf_counter() - t0) * 1000)
        
        print(f"\n{label}:")
        print(f"  DB exec (EXPLAIN ANALYZE): {db_ms:.2f} ms")
        print(f"  Round-trip avg: {sum(times)/len(times):.2f} ms (min={min(times):.2f}, max={max(times):.2f})")
        print(f"  Plan: {expl[0].strip()}")
