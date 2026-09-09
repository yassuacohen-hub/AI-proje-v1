"""normalize_company_name fonksiyonunu test et."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from web_app import normalize_company_name, extract_trade_name

# Test 1: Normal isim
name1 = "DUNDAR ELEKTRIK SANAYI"
print(f"Test 1 (normal): {repr(normalize_company_name(name1))}")

# Test 2: Newline iceren isim
name2 = "HASRET BUSRA KARABAY SIGORTA ARACILIK HIZMETLERI LIMI TED\n SIRKETI"
print(f"Test 2 (newline): {repr(normalize_company_name(name2))}")

# Test 3: extract_trade_name
name3 = "ARITES METAL SANAYI VE TICARET LTD.STI."
print(f"Test 3 (trade): {repr(extract_trade_name(name3))}")

# Test 4: Newline iceren trade_name
name4 = "HASRET BUSRA KARABAY SIGORTA ARACILIK HIZMETLERI LIMI TED\n SIRKETI"
print(f"Test 4 (trade+newline): {repr(extract_trade_name(name4))}")