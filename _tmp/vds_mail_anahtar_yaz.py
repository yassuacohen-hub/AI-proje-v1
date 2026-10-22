# -*- coding: utf-8 -*-
"""VDS app .env'e mail anahtarlari yazar (PO onayi 21.10: 'vds az onay', Secenek A).
D-380: deger ASLA yazdirilmaz; yalniz ad + DOLU/BOS. Mevcut anahtar ezilmez. Once yedek.
ponytail: tek seferlik; kalici akis gerekirse Docker secret / ortam yonetimine tasi.
"""
import json
import subprocess
from pathlib import Path

ENV = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\.env")
ADLAR = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM",
         "BREVO_API_KEY", "MAILERLITE_API_KEY"]  # SENDER_* yok: hesap askida (karar)
E = {}
for ln in ENV.read_text(encoding="utf-8-sig").splitlines():
    ln = ln.strip()
    if ln and not ln.startswith("#") and "=" in ln:
        k, _, v = ln.partition("=")
        E[k.strip()] = v.strip().strip('"').strip("'")
veri = {k: E[k] for k in ADLAR if E.get(k)}

UZAK = '''
import json, sys, shutil, time
from pathlib import Path
p = Path(r"C:\\Hugin_insights\\Apps\\huginn-data-insights\\.env")
veri = json.loads(%r)
mevcut = p.read_text(encoding="utf-8-sig") if p.exists() else ""
if p.exists():
    shutil.copy2(p, p.with_name(".env.bak_" + time.strftime("%%Y%%m%%d_%%H%%M%%S")))
var = {l.split("=",1)[0].strip() for l in mevcut.splitlines() if "=" in l and not l.strip().startswith("#")}
eklenen = []
out = mevcut if (not mevcut or mevcut.endswith("\\n")) else mevcut + "\\n"
for k, v in veri.items():
    if k in var:
        continue
    out += k + "=" + v + "\\n"
    eklenen.append(k)
p.write_text(out, encoding="utf-8", newline="\\n")
son = {l.split("=",1)[0].strip(): bool(l.split("=",1)[1].strip()) for l in out.splitlines() if "=" in l and not l.strip().startswith("#")}
print("eklenen:", eklenen)
for k in %r:
    print(k, "DOLU" if son.get(k) else "YOK/BOS")
''' % (json.dumps(veri), ADLAR)

r = subprocess.run(["ssh", "-o", "BatchMode=yes", "huginn-vds", "py.exe", "-3", "-X", "utf8", "-"],
                   input=UZAK.encode("utf-8"), capture_output=True, timeout=60)
print("yerel_dolu:", sorted(veri))
print(r.stdout.decode("utf-8", "replace"))
print("rc", r.returncode, r.stderr.decode("utf-8", "replace")[:300])
