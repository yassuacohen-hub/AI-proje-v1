from sqlalchemy import create_engine, text
import os
import re
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

# Turkish character fixes - map common mojibake patterns to correct characters
replacements = {
    # Common UTF-8 double-encoding / mojibake patterns
    'Ã§': 'ç', 'Ã¼': 'ü', 'Ä±': 'ı', 'ÄŸ': 'ğ', 'ÅŸ': 'ş', 'Ã¶': 'ö',
    'Ã‡': 'Ç', 'Ãœ': 'Ü', 'Ä°': 'İ', 'Ä': 'Ğ', 'ÅŸ': 'Ş', 'Ã–': 'Ö',
    'Ã¢': 'â', 'Ã¢': 'â',
    'Đ': 'Ğ', 'đ': 'ğ',
    'Ý': 'İ', 'ý': 'ı',
    'ÅŸ': 'ş', 'Å': 'İ', 'Ÿ': 'ş', 'ž': 'ş',
    # Additional common patterns
    'Ã§': 'ç', 'Ã¼': 'ü', 'Ä±': 'ı', 'ÄŸ': 'ğ', 'ÅŸ': 'ş', 'Ã¶': 'ö',
    'Ã‡': 'Ç', 'Ãœ': 'Ü', 'Ä°': 'İ', 'Ä': 'Ğ', 'ÅŸ': 'Ş', 'Ã–': 'Ö',
}

def fix_mojibake(text: str) -> str:
    if not text:
        return text
    result = text
    # First fix known mojibake patterns
    for wrong, correct in replacements.items():
        result = result.replace(wrong, correct)
    # Also handle the replacement character
    result = result.replace('\uFFFD', 'i')  # common for ı
    return result

with engine.connect() as conn:
    # Update source_records raw_name
    rows = conn.execute(text("""
        SELECT source_record_id, raw_name
        FROM source_records
        WHERE company_id IS NULL
    """)).fetchall()
    
    print(f"Processing {len(rows)} orphan records...")
    
    updated = 0
    for row in rows:
        src_id = row.source_record_id
        raw_name = row.raw_name
        if raw_name:
            fixed = fix_mojibake(raw_name)
            if fixed != raw_name:
                conn.execute(
                    text("UPDATE source_records SET raw_name = :name WHERE source_record_id = :id"),
                    {"name": fixed, "id": src_id}
                )
                updated += 1
    
    print(f"Updated {updated} records")
    conn.commit()
    
    # Verify
    rows = conn.execute(text("""
        SELECT raw_name FROM source_records WHERE company_id IS NULL LIMIT 10
    """)).fetchall()
    print("\nSample after fix:")
    for r in rows:
        print(f"  {r[0]}")