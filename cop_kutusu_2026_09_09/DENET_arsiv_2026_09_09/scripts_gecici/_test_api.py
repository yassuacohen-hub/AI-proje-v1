import json
import urllib.request

r = urllib.request.urlopen('http://127.0.0.1:8000/api/companies?limit=5&api_key=test-key-123')
d = json.loads(r.read().decode('utf-8'))
for item in d['items']:
    print('legal:', item['legal_name'])
    print('trade:', item['trade_name'])
    print()