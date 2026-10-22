"""ajan-chat.jsonl satirlari JSON-parse edilebiliyor mu."""
import json
import sys

yol = sys.argv[1]
n = hata = 0
for i, l in enumerate(open(yol, encoding="utf-8-sig"), 1):
    l = l.strip()
    if not l:
        continue
    try:
        json.loads(l)
        n += 1
    except Exception as e:
        hata += 1
        print("HATA satir", i, e)
print("jsonl", n, "ok,", hata, "hata")
sys.exit(1 if hata else 0)
