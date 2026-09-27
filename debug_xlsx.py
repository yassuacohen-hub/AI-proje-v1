import openpyxl
from pathlib import Path

def clean_turkish_chars(text: str) -> str:
    if not text:
        return ""
    replacements = {
        'â': 'a', 'Â': 'A',
        'ı': 'i', 'İ': 'I',
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C',
        'ÅŸ': 'ş', 'Å': 'İ', 'Ÿ': 'ş', 'ž': 'ş',
        'Đ': 'Ğ', 'đ': 'ğ', 'Ý': 'İ', 'ý': 'ı',
        'Ö': 'Ö', 'ö': 'ö', 'Ü': 'Ü', 'ü': 'ü',
        'Ç': 'Ç', 'ç': 'ç',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()

def normalize_nace_code(code: str) -> str:
    if not code:
        return ""
    code = str(code).strip()
    if '.' not in code and code.isdigit():
        if len(code) == 6:
            return f"{code[:2]}.{code[2:4]}.{code[4:]}"
        elif len(code) == 4:
            return f"{code[:2]}.{code[2:]}"
        elif len(code) == 2:
            return code
    return code

def extract_level(code: str) -> int:
    if not code:
        return 0
    code = str(code).strip()
    dots = code.count('.')
    if dots == 2:
        return 6
    elif dots == 1:
        return 4
    elif dots == 0 and code.isdigit():
        if len(code) == 2:
            return 2
        elif len(code) == 1:
            return 1
    return 0

def extract_parent_code(code: str):
    if not code:
        return None
    code = str(code).strip()
    dots = code.count('.')
    if dots >= 2:
        parts = code.split('.')
        return '.'.join(parts[:2])
    elif dots == 1:
        parts = code.split('.')
        return parts[0]
    elif code.isdigit() and len(code) == 2:
        return None
    elif len(code) == 1:
        return None
    return None

xlsx_path = Path('data/nace/sektor_meslek_nace_2026-05_resmi.xlsx')
wb = openpyxl.load_workbook(xlsx_path)
ws = wb.active

rows_data = []
parent_l4_info = {}
parent_l2_info = {}
sector_letters = set()
sector_group_map = {}
existing_codes = set()

for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
    sektor_kodu = clean_turkish_chars(str(row[0])) if row[0] else ""
    sektor_tanim = clean_turkish_chars(str(row[1])) if row[1] else ""
    meslek_kodu = clean_turkish_chars(str(row[2])) if row[2] else ""
    meslek_tanim = clean_turkish_chars(str(row[3])) if row[3] else ""
    nace_kodu_raw = str(row[4]).strip() if row[4] else ""
    nace_tanim = clean_turkish_chars(str(row[5])) if row[5] else ""
    
    if not nace_kodu_raw:
        continue
        
    nace_code = normalize_nace_code(nace_kodu_raw)
    if not nace_code:
        continue
    
    level = extract_level(nace_code)
    parent_code = extract_parent_code(nace_code)
    
    if level == 1 and sektor_kodu:
        sector_letters.add(sektor_kodu.upper())
        sector_group_map[nace_code] = sektor_tanim
    
    if parent_code:
        sector_group_map[parent_code] = sektor_tanim
    
    if parent_code:
        parent2 = extract_parent_code(parent_code)
        if parent2:
            sector_group_map[parent2] = sektor_tanim
    
    # 6 haneli kod kaydı
    rows_data.append({
        'nace_code': nace_code,
        'version': '2026.01.01_Mayis2026',
        'level': level,
        'parent_code': parent_code,
        'title': nace_tanim,
        'sector_group': sektor_tanim,
        'is_manufacturing': False,
        'source': 'xlsx_resmi',
    })
    
    # Parent kodlarını topla
    if level == 6 and parent_code:
        if parent_code not in parent_l4_info:
            parent_l4_info[parent_code] = {
                'title': meslek_tanim,
                'sector_group': sektor_tanim
            }
        parent2 = extract_parent_code(parent_code)
        if parent2 and parent2 not in parent_l2_info:
            parent_l2_info[parent2] = {
                'title': sektor_tanim,
                'sector_group': ''
            }
    elif level == 4 and parent_code:
        if parent_code not in parent_l2_info:
            parent_l2_info[parent_code] = {
                'title': meslek_tanim,
                'sector_group': ''
            }

print(f"Total rows_data: {len(rows_data)}")
print(f"parent_l4_info keys: {len(parent_l4_info)}")
if '47.79' in parent_l4_info:
    print(f"47.79 in parent_l4_info: {parent_l4_info['47.79']}")
else:
    print("47.79 NOT in parent_l4_info")

# Parent level 4 kodları ekle
for p4, info in parent_l4_info.items():
    rows_data.append({
        'nace_code': p4,
        'version': '2026.01.01_Mayis2026',
        'level': 4,
        'parent_code': extract_parent_code(p4),
        'title': info['title'],
        'sector_group': info['sector_group'],
        'is_manufacturing': False,
        'source': 'xlsx_derived',
    })

# Check 47.79 in final rows_data
for r in rows_data:
    if r['nace_code'] == '47.79':
        print(f"47.79 in rows_data: title='{r['title']}', sector_group='{r['sector_group']}', source={r['source']}")
        break
else:
    print("47.79 NOT in final rows_data")