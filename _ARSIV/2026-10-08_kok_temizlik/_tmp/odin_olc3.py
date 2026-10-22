import json, re
from pathlib import Path
R = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
S = [json.loads(s) for s in (R/"data/odin_injection_test_log.jsonl").read_text(encoding="utf-8").splitlines() if s.strip()]
L = []
p = lambda *a: L.append(" ".join(str(x) for x in a))
k3 = S[218:258]
yk = lambda s: s.get("yanit_kesit", "")
for s in k3:
    if s["tur"] == "zararli" and not s.get("reddetti"):
        p("KOSU3 zararli red DEGIL:", s["id"], "basarili", s["basarili"], "sizdirdi", s.get("sizdirdi"), "ihlal", s.get("kural_ihlal"), repr(yk(s)[:200]))
    if not s["basarili"]:
        p("KOSU3 basarisiz:", s["id"], s["tur"], "ihlal", s.get("kural_ihlal"), repr(yk(s)[:160]))
# kosu 3-4'te eksik senaryo id'leri (46 vs 40)
k4 = S[258:298]
sen_ids = None
p("SATIR 256 tam:", json.dumps({k: v for k, v in S[255].items() if k != "prompt"}, ensure_ascii=False)[:500])
src = (R/"scripts/odin_prompt_injection_test.py").read_text(encoding="utf-8").splitlines()
i = next(n for n, l in enumerate(src) if l.startswith("def karar_ver"))
p("--- karar_ver ---"); [p(f"{n+1}: {l}") for n, l in enumerate(src[i:i+62], i)]
sen = json.loads((R/"data/odin_injection_test_scenarios.json").read_text(encoding="utf-8"))
sl = sen if isinstance(sen, list) else sen.get("senaryolar", sen.get("scenarios"))
s7 = [s for s in sl if s["id"] == "satis-07"][0]
p("SATIS-07 senaryo:", json.dumps(s7, ensure_ascii=False)[:700])
sen_ids = {s["id"] for s in sl}
p("KOSU3 eksik id:", sorted(sen_ids - {s["id"] for s in k3}))
p("KOSU4 eksik id:", sorted(sen_ids - {s["id"] for s in k4}))
p("olcum=birim id:", sorted(s["id"] for s in sl if s.get("olcum") == "birim"))
j = next(n for n, l in enumerate(src) if l.startswith("def kural_kontrol"))
p("--- kural_kontrol ---"); [p(f"{n+1}: {l}") for n, l in enumerate(src[j:j+34], j)]
# rapor dosyalari son 30 satir
for f in ("TEST-ODIN-HAKEM-ESIK-01_rapor_2026-10-10_test.md", "TEST-ODIN-PROMPT-INJECTION_rapor_2026-10-21_test.md"):
    t = (R/"data/orchestrator"/f).read_text(encoding="utf-8").splitlines()
    p(f"--- {f} ({len(t)} satir) ---"); [p(l) for l in t[:45]]
Path(r"c:\Huginn Data Projesi\_tmp\odin_olc3_out.txt").write_text("\n".join(L), encoding="utf-8")
print("ok")
