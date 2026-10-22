import urllib.request as u  
for yol in ['/v1/models','/v1/v1/models','/models','/v1/v1/messages']:  
    try:  
        r=u.urlopen('http://127.0.0.1:20128'+yol,timeout=25); print('OK  ',yol,r.status,len(r.read()),'b')  
    except Exception as e: print('HATA',yol,str(e)[:58])  
