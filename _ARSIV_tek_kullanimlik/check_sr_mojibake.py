from sqlalchemy import create_engine, text
import os
import re
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

# Turkish character fixes
replacements = {
    'ı': 'i', 'İ': 'I',
    'ğ': 'g', 'Ğ': 'G',
    'ü': 'u', 'Ü': 'U',
    'ş': 's', 'Ş': 'S',
    'ö': 'o', 'Ö': 'O',
    'ç': 'c', 'Ç': 'C',
    'â': 'a', 'Â': 'A',
    # Common mojibake patterns
    'Đ': 'Ğ', 'đ': 'ğ',
    'Ý': 'İ', 'ý': 'ı',
    'ÅŸ': 'ş', 'Å': 'İ', 'Ÿ': 'ş', 'ž': 'ş',
    'Ã¶': 'ö', 'Ã¼': 'ü', 'Ã§': 'ç', 'Ä±': 'ı', 'ÄŸ': 'ğ', 'ÅŸ': 'ş',
    'Å': 'İ', 'Ÿ': 'ş',
}

def fix_mojibake(text: str) -> str:
    if not text:
        return text
    result = text
    for wrong, correct in replacements.items():
        result = result.replace(wrong, correct)
    return result

with engine.connect() as conn:
    # First, check how many records have mojibake
    rows = conn.execute(text("""
        SELECT source_record_id, raw_name
        FROM source_records
        WHERE raw_name LIKE '%�%' OR raw_name LIKE '%Đ%' OR raw_name LIKE '%Ý%' 
           OR raw_name LIKE '%Å%' OR raw_name LIKE '%Ã%' OR raw_name LIKE '%Ä%'
        LIMIT 10
    """)).fetchall()
    print(f"Records with mojibake: {len(rows)}")
    for r in rows:
        print(f"  {r[0]} | {r[1]}")