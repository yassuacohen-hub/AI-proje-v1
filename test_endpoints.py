import httpx

eps = [
    'https://tobb.org.tr/webservis',
    'https://tobb.org.tr/api',
    'https://tobb.org.tr/ws',
    'https://api.tobb.org.tr',
    'https://webservis.tobb.org.tr',
]

for e in eps:
    try:
        r = httpx.get(e, timeout=5.0, verify=False, follow_redirects=False)
        print(e, r.status_code, r.headers.get('Location', 'no redirect'))
    except Exception as ex:
        print(e, 'ERROR', ex)