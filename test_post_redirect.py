import httpx

url = 'https://tobb.org.tr'
payload = {
    'Metod': 'BakiyeSorgula',
    'Kodu': '[REDACTED-ENV]',
    'Sifre': '[REDACTED-ENV]'
}
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

# Test POST with follow_redirects=True to see final response
r = httpx.post(url, json=payload, headers=headers, timeout=30.0, verify=False, follow_redirects=True)
print('Status:', r.status_code)
print('Final URL:', r.url)
print('Content-Type:', r.headers.get('Content-Type'))
print('Body:', r.text[:2000])