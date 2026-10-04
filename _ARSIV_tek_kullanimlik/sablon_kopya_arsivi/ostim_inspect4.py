import requests, re
from bs4 import BeautifulSoup
BASE_URL = "https://www.ostim.org.tr"
slug = "sihhat-grup-is-guvenligi-danismanlik-ticltdsti"
resp = requests.get(BASE_URL + "/firmalar/" + slug, headers={"User-Agent": "AnkaraB2B-Bot/1.0 (research@example.com)"}, timeout=30)
soup = BeautifulSoup(resp.text, "html.parser")
text = resp.text
# Find the firm's website link context
for kw in ["sihhatgrup.com.tr", "ostimonline.com"]:
    pos = 0
    low = text.lower()
    while True:
        idx = low.find(kw.lower(), pos)
        if idx == -1: break
        print("=== %s @ %d ===" % (kw, idx))
        print(repr(text[max(0,idx-300):idx+200].replace(chr(10)," ").replace(chr(13)," ")))
        print()
        pos = idx + 1
