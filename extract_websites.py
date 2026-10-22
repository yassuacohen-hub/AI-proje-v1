import json

with open('c:\\Huginn Data Projesi\\osb_harita_verisi.json') as f:
    data = json.load(f)

websites = set()
for city, city_data in data['iller'].items():
    for entry in city_data['veri']:
        web = entry.get('web', '')
        if web:
            websites.add(web)

print(f'Toplam unique web sitesi: {len(websites)}')
sorted_websites = sorted(websites)
for w in sorted_websites:
    print(w)