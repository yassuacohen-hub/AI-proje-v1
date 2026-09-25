import re
t = open('C:/Huginn Data Projesi/Huginn Data Insights/web_dashboard/charts.py', encoding='utf-8').read()
open('C:/Users/yasin/AppData/Local/Temp/kilo/charts_py.txt', 'w', encoding='utf-8').write(t)
print('wrote', len(t), 'chars,', t.count(chr(10)), 'lines')
for m in re.finditer(r'KATEGORI_RENK|KATEGORILER', t):
    s = m.start()
    ls = t.rfind(chr(10), 0, s) + 1
    le = t.find(chr(10), s)
    print('  line', t[:s].count(chr(10))+1, repr(t[ls:le]))