@echo off
chcp 65001 >nul
cd /d c:\Huginn Data Projesi
set DOMAINS=anadoluosb.org.tr dokumculerosb.org.tr aso2osb.org.tr aosb.org.tr hab.org.tr cubuktdiosb.org ivedikosb.org.tr baskentosb.org www.baskentosb.org.tr beyosb.org.tr mobilyacilarosb.com ostim.org.tr posb.org.tr ptoosb.org.tr sereflikochisarosb.org.tr
> _tmp\osb_curl.txt echo OSB WEB ADRES OLCUMU (curl -sI, timeout 12)
for %%D in (%DOMAINS%) do (
  for /f "tokens=*" %%C in ('curl -s -o nul -w "%%{http_code} %%{url_effective}" -m 12 -A "Mozilla/5.0" "https://%%D" 2^>nul') do (
    echo %%D = %%C>> _tmp\osb_curl.txt
  )
)
type _tmp\osb_curl.txt
