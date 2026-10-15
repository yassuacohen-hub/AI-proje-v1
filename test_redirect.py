import httpx

url = 'https://tobb.org.tr'

# Test without following redirects
r = httpx.get(url, timeout=10.0, verify=False, follow_redirects=False)
print('GET without redirects:')
print('  Status:', r.status_code)
print('  Location:', r.headers.get('Location'))
print('  Headers:', dict(r.headers))

# Test with following redirects
r2 = httpx.get(url, timeout=10.0, verify=False, follow_redirects=True)
print('\nGET with redirects:')
print('  Status:', r2.status_code)
print('  Final URL:', r2.url)
print('  Body:', r2.text[:500])

# Test POST
payload = {
    'Metod': 'BakiyeSorgula',
    'Kodu': '[REDACTED-ENV]',
    'Sifre': '[REDACTED-ENV]'
}
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

r3 = httpx.post(url, json=payload, headers=headers, timeout=30.0, verify=False, follow_redirects=False)
print('\nPOST without redirects:')
print('  Status:', r3.status_code)
print('  Location:', r3.headers.get('Location'))
print('  Body:', r3.text[:500])

r4 = httpx.post(url, json=payload, headers=headers, timeout=30.0, verify=False, follow_redirects=True)
print('\nPOST with redirects:')
print('  Status:', r4.status_code)
print('  Final URL:', r4.url)
print('  Body:', r4.text[:500])