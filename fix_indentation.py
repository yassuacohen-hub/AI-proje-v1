# This script fixes the indentation of the except APIError in render_api_management
import sys

file_path = 'web_dashboard/tabs/admin_extras.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "except APIError:" that is inside the render_api_management function
# We'll look for the line and adjust its indentation if it has 8 spaces
for i, line in enumerate(lines):
    if line.strip() == 'except APIError:':
        # Check the indentation: we expect it to be 4 spaces, but if it's 8, we reduce by 4
        if line.startswith('        '):  # 8 spaces
            lines[i] = '    ' + line[8:]  # replace 8 spaces with 4
            print(f"Fixed except indentation at line {i+1}")
        break

# Also fix the string "API kullan�m kayd� yok." to "API kullanım kaydı yok."
# and "L�tfen giri� yap�n veya yetkili olun" to "Lütfen giriş yapın veya yetkili olun"
# We'll do a simple replace for known corrupted strings.
content = ''.join(lines)
content = content.replace('API kullan�m kayd� yok.', 'API kullanım kaydı yok.')
content = content.replace('L�tfen giri� yap�n veya yetkili olun', 'Lütfen giriş yapın veya yetkili olun')
# Also fix the corruption in the user management function strings if any
content = content.replace('onayland�', 'onaylandı')
content = content.replace('ba�ar�s�z', 'başarısız')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("File fixed")
