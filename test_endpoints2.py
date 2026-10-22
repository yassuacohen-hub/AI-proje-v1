import httpx

# TOBB web servis common paths
eps = [
    'https://tobb.org.tr/TTSGWebServis',
    'https://tobb.org.tr/Service',
    'https://tobb.org.tr/wsdl',
    'https://tobb.org.tr/WebServis',
    'https://tobb.org.tr/Sayfalar/WebServis.aspx',
    'https://tobb.org.tr/Sayfalar/WebServis.php',
    'https://tobb.org.tr/api/ws',
    'https://tobb.org.tr/rest',
    'https://tobb.org.tr/json',
    'https://tobb.org.tr/SirketKarti',
    'https://tobb.org.tr/ws/SirketKarti',
]

for e in eps:
    try:
        r = httpx.get(e, timeout=5.0, verify=False, follow_redirects=False)
        print(e, r.status_code, r.headers.get('Location', 'no redirect')[:80] if r.headers.get('Location') else 'no redirect')
    except Exception as ex:
        print(e, 'ERROR', type(ex).__name__)