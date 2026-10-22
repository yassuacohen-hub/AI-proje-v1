"""D-260: salih teslim ozetlerini canli olc. Cikti: _tmp/odin_olc_out.txt"""
import json, re, sys, glob, subprocess
from pathlib import Path
from collections import Counter

R = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
OUT = Path(r"c:\Huginn Data Projesi\_tmp\odin_olc_out.txt")
L = []
p = lambda *a: L.append(" ".join(str(x) for x in a))

log = R / "data/odin_injection_test_log.jsonl"
satirlar = [json.loads(s) for s in log.read_text(encoding="utf-8").splitlines() if s.strip()]
p("LOG satir:", len(satirlar), "(iddia: 298; HAKEM iddiasi 256)")
p("anahtarlar:", sorted(satirlar[-1].keys()))

# kosulari zaman damgasina gore grupla
def z(s): return (s.get("zaman") or s.get("timestamp") or s.get("ts") or "")[:16]
grp = Counter(z(s) for s in satirlar)
p("kosu gruplari (ilk16 zaman -> adet):")
for k, v in sorted(grp.items()): p("  ", k, v)

# son kosu = son grup
son_z = z(satirlar[-1])
son = [s for s in satirlar if z(s) == son_z]
p("SON KOSU zaman:", son_z, "adet:", len(son), "(iddia 46; satir 269-284 = 16?)")
idx = [i+1 for i, s in enumerate(satirlar) if z(s) == son_z]
p("  satir aralik:", idx[0], "-", idx[-1])

def say(kayitlar):
    c = Counter()
    for s in kayitlar:
        tur = s.get("tur") or s.get("kategori") or s.get("tip") or "?"
        c[("tur", tur)] += 1
        for k in ("reddetti", "sizinti", "ag_hatasi", "basarili", "gecti", "mesru"):
            if k in s: c[(k, bool(s[k]))] += 1
        if s.get("hata"): c[("hata", str(s["hata"])[:40])] += 1
        if s.get("ihlal") or s.get("ihlaller"): c[("ihlal_var", True)] += 1
    return c
p("SON KOSU sayim:")
for k, v in sorted(say(son).items(), key=str): p("  ", k, v)
p("ornek kayit:", json.dumps(son[0], ensure_ascii=False)[:600])

# satis-07
s7 = [s for s in son if "satis-07" in json.dumps(s, ensure_ascii=False)]
p("satis-07 son kosu:", len(s7), json.dumps(s7[0], ensure_ascii=False)[:500] if s7 else "-")

# mesru-02/03, s2-webtext-sifre son kosuda
for sid in ("mesru-02", "mesru-03", "s2-webtext-sifre", "inj-11", "inj-12"):
    m = [s for s in son if s.get("id") == sid or s.get("senaryo") == sid or s.get("senaryo_id") == sid]
    p(f"  {sid}: {len(m)} kayit", json.dumps({k: m[0][k] for k in m[0] if k not in ("yanit","prompt")}, ensure_ascii=False)[:300] if m else "")

# rapor dosyalari
p("RAPOR dosyalari:")
for g in glob.glob(str(R / "data/orchestrator/TEST-ODIN-*rapor*")): p("  ", Path(g).name)
# hub satiri
hub = (R / "hubs/VERI_KALITESI_HUB.md").read_text(encoding="utf-8")
p("HUB TEST-ODIN-HAKEM-ESIK-01:", "TEST-ODIN-HAKEM-ESIK-01" in hub, "| PROMPT-INJECTION:", "TEST-ODIN-PROMPT-INJECTION" in hub)
# retry kodu
src = (R / "scripts/odin_prompt_injection_test.py").read_text(encoding="utf-8")
p("_istek_gonder var:", "def _istek_gonder" in src, "| Retry-After:", "Retry-After" in src, "| deneme sayisi 5:", bool(re.search(r"range\(5\)|deneme\s*<\s*5|=\s*5\b", src)))
p("hakem soru metni:", re.findall(r"_llm_hakem_evet_mi\(([^)]*)\)", src)[:5])
# senaryo sayisi
sen = json.loads((R / "data/odin_injection_test_scenarios.json").read_text(encoding="utf-8"))
sen_l = sen if isinstance(sen, list) else sen.get("senaryolar", sen.get("scenarios", []))
p("SENARYO sayisi:", len(sen_l), "(iddia 46)")
p("  zararli:", sum(1 for s in sen_l if s.get("beklenen") == "red" or s.get("tur") in ("zararli","injection","prompt_injection")), " | turler:", Counter(s.get("tur") or s.get("kategori") for s in sen_l))

OUT.write_text("\n".join(L), encoding="utf-8")
print("yazildi", OUT)
