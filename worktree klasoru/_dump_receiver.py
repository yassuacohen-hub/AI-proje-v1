import re
t = open('C:/Huginn Data Projesi/Huginn Data Insights/scripts/apify_webhook_receiver.py', encoding='utf-8').read()
open('C:/Users/yasin/AppData/Local/Temp/kilo/receiver.txt', 'w', encoding='utf-8').write(t)
print('wrote', len(t), 'chars,', t.count(chr(10)), 'lines')
for m in re.finditer(r'(ERROR_LEDGER|WEBHOOK_EVENT_LOG|_processed_runs|DLQ|ERROR)', t):
    s = m.start()
    ls = t.rfind(chr(10), 0, s) + 1
    le = t.find(chr(10), s)
    print('  line', t[:s].count(chr(10))+1, repr(t[ls:le]))