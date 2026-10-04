# -*- coding: utf-8 -*-
"""VERI-SEKTOR-01: companies.sector_name ve companies.sector_source doldurma."""

import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

# Load dictionary
with open("data/sektor/sektor_sozluk.json", 'r', encoding='utf-8') as f:
    SEKTOR_SOZLUK = json.load(f)

print("Creating temp mapping table...")
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS tmp_sektor_map"))
    conn.execute(text("""
        CREATE TEMP TABLE tmp_sektor_map (
            sade VARCHAR(255) PRIMARY KEY,
            gosterim VARCHAR(255)
        )
    """))
    
    for entry in json.load(open("data/sektor/sektor_sozluk.json", encoding='utf-8')):
        conn.execute(text("""
            INSERT INTO tmp_sektor_map (sade, gosterim)
            VALUES (:sade, :gosterim)
            ON CONFLICT (sade) DO NOTHING
        """), {"sade": entry['sade'], "gosterim": entry['gosterim']})
    
    print("Created tmp_sektor_map with", conn.execute(text("SELECT COUNT(*) FROM tmp_sektor_map")).scalar(), "entries")

# Now do the population
print("Populating sector columns...")

with engine.begin() as conn:
    # Create temp table with best sector per company
    sql1 = """
        CREATE TEMP TABLE tmp_company_sector AS
        SELECT DISTINCT ON (c.company_id)
            c.company_id,
            s.norm as best_sector,
            s.source_list
        FROM companies c
        LEFT JOIN (
            SELECT 
                sr.company_id,
                n.norm,
                COUNT(*) as cnt,
                STRING_AGG(DISTINCT s.source_name, ', ') as source_list
            FROM (
                SELECT 
                    sr.company_id,
                    sr.raw_payload->>'sektor' as sektor,
                    s.source_name
                FROM source_records sr
                JOIN sources s ON sr.source_id = s.source_id
                WHERE sr.raw_payload->>'sektor' IS NOT NULL
                  AND sr.raw_payload->>'sektor' !~ '^[0-9]{1,2}\.\s*MESLEK\s+GRUBU$'
            ) sr
            CROSS JOIN LATERAL (SELECT regexp_replace(sektor, '\d+$', '') as norm) n
            JOIN sources s ON s.source_name = sr.source_name
            WHERE n.norm IS NOT NULL AND n.norm != ''
            GROUP BY sr.company_id, n.norm, s.source_name
        ) s ON c.company_id = s.company_id
        ORDER BY c.company_id, s.cnt DESC
    """
    conn.execute(text(sql1))
    
    print("Created tmp_company_sector")
    
    # Now update companies
    sql2 = """
        UPDATE companies c
        SET 
            sector_name = (
                SELECT m.gosterim 
                FROM tmp_sektor_map m 
                WHERE m.sade = t.best_sector
            ),
            sector_source = t.source_list
        FROM tmp_company_sector t
        WHERE c.company_id = t.company_id
          AND t.best_sector IS NOT NULL
    """
    conn.execute(text(sql2))
    
    # Check results
    total = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
    with_sector = conn.execute(text("SELECT COUNT(*) FROM companies WHERE sector_name IS NOT NULL")).scalar()
    print(f"Total: {total}, With sector: {with_sector}")

if __name__ == "__main__":
    import os
    import json
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Load dictionary
    with open("data/sektor/sektor_sozluk.json", 'r', encoding='utf-8') as f:
        SEKTOR_SOZLUK = json.load(f)

    print("Creating temp mapping table...")
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS tmp_sektor_map"))
        conn.execute(text("""
            CREATE TEMP TABLE tmp_sektor_map (
                sade VARCHAR(255) PRIMARY KEY,
                gosterim VARCHAR(255)
            )
        """))
        
        for entry in SEKTOR_SOZLUK:
            conn.execute(text("""
                INSERT INTO tmp_sektor_map (sade, gosterim)
                VALUES (:sade, :gosterim)
                ON CONFLICT (sade) DO NOTHING
            """), {"sade": entry['sade'], "gosterim": entry['gosterim']})
        
        print("Created tmp_sektor_map with", conn.execute(text("SELECT COUNT(*) FROM tmp_sektor_map")).scalar(), "entries")

    # Now do the population
    print("Populating sector columns...")

    with engine.begin() as conn:
        # Create temp table with best sector per company
        sql1 = """
            CREATE TEMP TABLE tmp_company_sector AS
            SELECT DISTINCT ON (c.company_id)
                c.company_id,
                s.norm as best_sector,
                s.source_list
            FROM companies c
            LEFT JOIN (
                SELECT 
                    sr.company_id,
                    n.norm,
                    COUNT(*) as cnt,
                    STRING_AGG(DISTINCT s.source_name, ', ') as source_list
                FROM (
                    SELECT 
                        sr.company_id,
                        sr.raw_payload->>'sektor' as sektor,
                        s.source_name
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE sr.raw_payload->>'sektor' IS NOT NULL
                      AND sr.raw_payload->>'sektor' !~ '^[0-9]{1,2}\.\s*MESLEK\s+GRUBU$'
                ) sr
                CROSS JOIN LATERAL (SELECT regexp_replace(sektor, '\d+$', '') as norm) n
                JOIN sources s ON s.source_name = sr.source_name
                WHERE n.norm IS NOT NULL AND n.norm != ''
                GROUP BY sr.company_id, n.norm, s.source_name
            ) s ON c.company_id = s.company_id
            ORDER BY c.company_id, s.cnt DESC
        """
        conn.execute(text(sql1))
        
        print("Created tmp_company_sector")
        
        # Now update companies
        sql2 = """
            UPDATE companies c
            SET 
                sector_name = (
                    SELECT m.gosterim 
                    FROM tmp_sektor_map m 
                    WHERE m.sade = t.best_sector
                ),
                sector_source = t.source_list
            FROM tmp_company_sector t
            WHERE c.company_id = t.company_id
              AND t.best_sector IS NOT NULL
        """
        conn.execute(text(sql2))
        
        # Check results
        total = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
        with_sector = conn.execute(text("SELECT COUNT(*) FROM companies WHERE sector_name IS NOT NULL")).scalar()
        print(f"Total: {total}, With sector: {with_sector}")

if __name__ == "__main__":
    import os
    import json
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Load dictionary
    with open("data/sektor/sektor_sozluk.json", 'r', encoding='utf-8') as f:
        SEKTOR_SOZLUK = json.load(f)

    print("Creating temp mapping table...")
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS tmp_sektor_map"))
        conn.execute(text("""
            CREATE TEMP TABLE tmp_sektor_map (
                sade VARCHAR(255) PRIMARY KEY,
                gosterim VARCHAR(255)
            )
        """))
        
        for entry in SEKTOR_SOZLUK:
            conn.execute(text("""
                INSERT INTO tmp_sektor_map (sade, gosterim)
                VALUES (:sade, :gosterim)
                ON CONFLICT (sade) DO NOTHING
            """), {"sade": entry['sade'], "gosterim": entry['gosterim']})
        
        print("Created tmp_sektor_map with", conn.execute(text("SELECT COUNT(*) FROM tmp_sektor_map")).scalar(), "entries")

    # Now do the population
    print("Populating sector columns...")

    with engine.begin() as conn:
        # Create temp table with best sector per company
        sql1 = """
            CREATE TEMP TABLE tmp_company_sector AS
            SELECT DISTINCT ON (c.company_id)
                c.company_id,
                s.norm as best_sector,
                s.source_list
            FROM companies c
            LEFT JOIN (
                SELECT 
                    sr.company_id,
                    n.norm,
                    COUNT(*) as cnt,
                    STRING_AGG(DISTINCT s.source_name, ', ') as source_list
                FROM (
                    SELECT 
                        sr.company_id,
                        sr.raw_payload->>'sektor' as sektor,
                        s.source_name
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE sr.raw_payload->>'sektor' IS NOT NULL
                      AND sr.raw_payload->>'sektor' !~ '^[0-9]{1,2}\.\s*MESLEK\s+GRUBU$'
                ) sr
                CROSS JOIN LATERAL (SELECT regexp_replace(sektor, '\d+$', '') as norm) n
                JOIN sources s ON s.source_name = sr.source_name
                WHERE n.norm IS NOT NULL AND n.norm != ''
                GROUP BY sr.company_id, n.norm, s.source_name
            ) s ON c.company_id = s.company_id
            ORDER BY c.company_id, s.cnt DESC
        """
        conn.execute(text(sql1))
        
        print("Created tmp_company_sector")
        
        # Now update companies
        sql2 = """
            UPDATE companies c
            SET 
                sector_name = (
                    SELECT m.gosterim 
                    FROM tmp_sektor_map m 
                    WHERE m.sade = t.best_sector
                ),
                sector_source = t.source_list
            FROM tmp_company_sector t
            WHERE c.company_id = t.company_id
              AND t.best_sector IS NOT NULL
        """
        conn.execute(text(sql2))
        
        # Check results
        total = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
        with_sector = conn.execute(text("SELECT COUNT(*) FROM companies WHERE sector_name IS NOT NULL")).scalar()
        print(f"Total: {total}, With sector: {with_sector}")

if __name__ == "__main__":
    import os
    import json
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    main()