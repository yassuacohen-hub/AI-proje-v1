import json
from pathlib import Path

lines = Path('C:/Projeler/Huginn Data Insights/data/aso/aso_full.jsonl').read_text(encoding='utf-8').splitlines()
print(f'Total ASO lines: {len(lines)}')
if lines:
    entry = json.loads(lines[0])
    print(f'unvan: {entry.get("unvan", "")[:60]}')
    print(f'Keys: {list(entry.keys())}')
    print(f'ticaretSicilNo: {entry.get("ticaretSicilNo")}')
    print(f'naceKod: {entry.get("naceKod")}')
    print(f'adres: {entry.get("adres", "")[:80]}')
    print(f'telefonler: {entry.get("telefonler", [])}')
    print(f'emailler: {entry.get("emailler", [])}')
    print(f'web_sitesi: {entry.get("web_sitesi", "")}')
    print(f'vergiNo: {entry.get("vergiNo", "")}')