with open(r'C:\Huginn Data Projesi\Huginn Data Insights\web_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The issue is at lines 3875-3882:
# 3874: '    except Exception as e:\n'  (extra except - REMOVE)
# 3875: '    @app.post("/api/admin/mfa/disable")\n' (decorator)
# 3878: '    req: dict,\n' (params without def line!)
# 3879: '    request: Request,\n'
# 3880: '    _auth: str = Depends(require_admin_role)\n'
# 3881: '):\n' (closing params but no def line!)

# Fix: Remove the extra except at line 3876 (index 3875)
# Insert missing 'def api_admin_mfa_disable(\n' before the decorator at line 3876 (index 3875)

# First, verify current state
with open(r'C:\Huginn Data Projesi\Huginn Data Insights\web_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Before fix:')
for i in range(3872, 3885):
    print(f'{i}: indent={len(lines[i])-len(lines[i].lstrip())} {repr(lines[i])}')

# Remove the extra except at index 3875 (line 3876)
del lines[3875]

# Insert missing function definition before the decorator (now at index 3875 after deletion)
lines.insert(3875, 'def api_admin_mfa_disable(\n')

with open(r'C:\Huginn Data Projesi\Huginn Data Insights\web_app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed')