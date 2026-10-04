import json
with open('src/company_master/schema/migrations/schema_versions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print('Current version:', data.get('current_version'))
print('Last applied:', data.get('last_applied'))
for m in data['migrations'][-10:]:
    print(f"  {m['version']}: {m['file']} - {m.get('note', '')}")