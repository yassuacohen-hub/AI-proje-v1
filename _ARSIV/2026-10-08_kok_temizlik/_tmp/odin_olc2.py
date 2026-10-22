import json
from pathlib import Path
from datetime import datetime
from collections import Counter
R = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
S = [json.loads(s) for s in (R/"data/odin_injection_test_log.jsonl").read_text(encoding="utf-8").splitlines() if s.strip()]
L = []
p = lambda *a: L.append(" ".join(str(x) for x in a))
# kosu = 10dk+ bosluk
runs, cur, prev = [], [], None
for i, s in enumerate(S, 1):
    t = datetime.fromisoformat(s["timestamp"])
    if prev and (t - prev).total_seconds() > 600:
        runs.append(cur); cur = []
    cur.append((i, s)); prev = t
runs.append(cur)
for k, r in enumerate(runs, 1):
    ss = [s for _, s in r]
    c = Counter()
    for s in ss:
        tur = s["tur"]
        c[f"{tur}_n"] += 1
        if s.get("ag_hatasi"): c["ag_hatasi"] += 1
        if s.get("sizdirdi"): c["sizdirdi"] += 1
        if tur == "zararli" and s.get("reddetti"): c["zararli_red"] += 1
        if tur == "mesru" and s.get("reddetti") and not s.get("red_beklenmez"): c["mesru_red"] += 1
        if tur == "mesru" and s.get("reddetti") and s.get("red_beklenmez"): c["mesru_red_izleme"] += 1
        if not s.get("basarili"): c["basarisiz"] += 1; c[f"basarisiz:{s['id']}"] += 1
    p(f"KOSU {k}: satir {r[0][0]}-{r[-1][0]} n={len(r)} {ss[0]['timestamp'][:16]}..{ss[-1]['timestamp'][:16]}")
    p("   ", dict(sorted(c.items())))
    ids = Counter(s["id"] for s in ss)
    dup = {i: n for i, n in ids.items() if n > 1}
    p("    tekil id:", len(ids), "| tekrar:", dup if dup else "-")
# satir 269-284 iddiasi
blk = S[268:284]
p("SATIR 269-284:", len(blk), Counter(s["tur"] for s in blk), "ag_hatasi:", sum(bool(s.get("ag_hatasi")) for s in blk), "zaman", blk[0]["timestamp"][:16], blk[-1]["timestamp"][:16])
p("SATIR 256:", S[255]["id"], S[255]["timestamp"], S[255]["tur"], "reddetti", S[255]["reddetti"])
# satis-07 tum log
for i, s in enumerate(S, 1):
    if s["id"] == "satis-07":
        p(f"satis-07 satir {i} basarili={s['basarili']} reddetti={s['reddetti']} ihlal={s['kural_ihlal']} yanit={s['yanit_kesit'][:120]!r}")
Path(r"c:\Huginn Data Projesi\_tmp\odin_olc2_out.txt").write_text("\n".join(L), encoding="utf-8")
print("ok")
