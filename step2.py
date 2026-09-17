with open('docs/raporlar/roo_code/taslak_yapilandirma_2026-09-17.md', 'rb') as f:
    raw = f.read()
try:
    raw.decode('utf-8')
    print('REPORT UTF-8: VALID')
except UnicodeDecodeError as e:
    print(f'REPORT UTF-8: INVALID - {e}')

text = raw.decode('utf-8', errors='replace')
mojibake_markers = ['Ã', 'â€', 'Ã§', 'Ã¼']
found = [m for m in mojibake_markers if m in text]
if found:
    print(f'MOJIBAKE FOUND: {found}')
else:
    print('No obvious mojibake detected')
