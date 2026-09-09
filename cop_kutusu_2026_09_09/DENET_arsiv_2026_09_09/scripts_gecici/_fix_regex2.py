"""Regex pattern'ini düzelt - doğrudan satır numarasıyla."""
path = r'C:\Projeler\Huginn Data Insights\web_app.py'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Satır 38 (0-indexed: 37) - regex pattern
lines[37] = r"    cleaned = _re.sub(r'[\r\n\t]+', ' ', name)" + "\n"
print(f"Satır 38: {repr(lines[37])}")

# Satır 41 (0-indexed: 40) - \s{2,} pattern  
lines[40] = r"    cleaned = _re.sub(r'\s{2,}', ' ', cleaned)" + "\n"
print(f"Satır 41: {repr(lines[40])}")

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Kaydedildi.")

# Doğrula
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
    
# Kontrol et
if r"_re.sub(r'[\r\n\t]+'" in content:
    print("✓ Satır 38 doğru")
else:
    print("✗ Satır 38 hâlâ yanlış")

if r"_re.sub(r'\s{2,}'" in content:
    print("✓ Satır 41 doğru")
else:
    print("✗ Satır 41 hâlâ yanlış")