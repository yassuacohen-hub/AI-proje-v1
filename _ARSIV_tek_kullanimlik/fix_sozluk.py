with open('src/company_master/etl/sozluk_baslik_duzelt.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("        '\uFFFD': 'a', '\uFFFD': 'A',\n", "        'â': 'a', 'Â': 'A',\n")

with open('src/company_master/etl/sozluk_baslik_duzelt.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed sozluk_baslik_duzelt.py')