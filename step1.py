import json

with open('docs/roo_config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print("JSON VALID")
print(f"Models: {len(data.get('models', []))}")
print(f"Has fallback: {'fallback' in data}")
print(f"Has tabAutocomplete: {'tabAutocompleteModel' in data}")
print(f"Has contextProviders: {'contextProviders' in data}")
content = json.dumps(data)
if '9router' in content.lower() or '9Router' in content:
    print("WARNING: 9Router reference found!")
else:
    print("No 9Router reference - OK")
if 'reasoning' in content.lower() or ('thinking' in content.lower() and 'budget' in content.lower()):
    print("WARNING: reasoning/budget mention found in values")
else:
    print("D-48 compliant - no reasoning/budget reduction")
for m in data.get('models', []):
    print(f"  {m.get('title', 'N/A')}")
