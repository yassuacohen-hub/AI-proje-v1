import httpx

# Check the main page for API links
url = 'https://tobb.org.tr'
r = httpx.get(url, timeout=10.0, verify=False, follow_redirects=True)
print('Main page status:', r.status_code)

# Look for web service links in HTML
import re
links = re.findall(r'href=["\']([^"\']*(?:webservis|api|ws|service|wsdl)[^"\']*)["\']', r.text, re.IGNORECASE)
print('API/Webservice links found:')
for link in links:
    print(' ', link)

# Also check for form actions
forms = re.findall(r'action=["\']([^"\']*)["\']', r.text, re.IGNORECASE)
print('\nForm actions:')
for form in forms:
    print(' ', form)

# Check for any javascript API calls
js_urls = re.findall(r'["\']([^"\']*(?:tobb|api|webservis)[^"\']*\.(?:php|asmx|json|xml))["\']', r.text, re.IGNORECASE)
print('\nJS API URLs:')
for js in js_urls:
    print(' ', js)