import json, re
pats = json.load(open("_tmp/hayalet_pats.json", encoding="utf-8"))
# bos pattern'lere elle anahtar
pats.setdefault("SEC-MTLS-SERTIFIKALARI-CA-CERT-002", "")
ek = {
    "SEC-MTLS-SERTIFIKALARI-CA-CERT-002": r"mtls|ca\.crt|cert/key|sertifika üret",
    "DOC-FINANSAL-MODEL-VE-KARLILIK-ANA-014": r"finansal model|karlılık|investor|yatırımcı|ebitda|break.?even",
    "SEC-KVKK-BDDK-MASKELEME-VE-UYUMLUL-015": r"kvkk.*mask|bddk|pii|maskele",
}
for k, v in ek.items():
    pats[k] = v
docs = {"docx": "_tmp/docx_metin.txt", "guv": "yedekler/güvenlik full.md", "tas": "yedekler/tasinma-rehberi-v3.md"}
L = {k: open(v, encoding="utf-8", errors="ignore").read().splitlines() for k, v in docs.items()}
out = []
for tid, pat in pats.items():
    pat = pat.split(". TAMAMLANDI")[0].strip()
    if not pat:
        continue
    rx = re.compile(pat, re.I)
    out.append(f"\n===== {tid} | /{pat}/")
    for dk, lines in L.items():
        hits = [i for i, l in enumerate(lines) if rx.search(l)]
        out.append(f"-- {dk}: {len(hits)} satir")
        for i in hits[:6]:
            ctx = " ".join(x.strip() for x in lines[max(0, i-1):i+2])
            out.append(f"  {dk}:{i+1} | {ctx[:260]}")
open("_tmp/hayalet_belge_out.txt", "w", encoding="utf-8").write("\n".join(out))
print(len(out), "satir yazildi")
