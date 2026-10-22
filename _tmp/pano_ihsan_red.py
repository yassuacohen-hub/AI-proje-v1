# -*- coding: utf-8 -*-
"""Denetim reddi: kanitsiz 'done' iddia eden 5 yasu gorevini blocked'a cek (D-260)."""
import json, io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"Huginn Data Insights/data/orchestrator/task_board.json"
with open(P, encoding="utf-8") as f:
    tb = json.load(f)

SEBEB = {
    "ALTYAPI-VDS-DOCKER-01": "KANIT YOK: kanit_vds_docker.txt yok; docker ps/pg_isready cikti yok.",
    "ALTYAPI-SPACESHIP-DNS-01": "KANIT YOK: kanit_spaceship_dns.txt yok; nslookup cikti yok.",
    "ALTYAPI-KONG-MULTISITE-01": "KANIT YOK: kanit_kong_multisite.txt yok; kong.yml ornek IP'de (192.168.1.50), gercek VDS IP'si yok.",
    "UI-FIRMAARAMA-SEARCH-01": "KANIT YOK: page.tsx sadece statik link; arama bileseni/API cagrisi bulunamadi.",
    "ALTYAPI-ODEME-01": "KANIT YOK: odeme.py / routers v1 odeme / test_odeme.py hicbiri yok; iyzico+PayTR kodu yok.",
}
simdi = datetime.datetime.now().isoformat(timespec="seconds")
n = 0
for t in tb:
    tid = t.get("id")
    if tid in SEBEB and (t.get("durum") or "").lower() == "done":
        t["durum"] = "aktif"
        t["bitis"] = None
        t["not"] = (str(t.get("not") or "") + " | IHSAN DENETIM REDDI " + simdi +
                    " (D-260 beyan != kanit): " + SEBEB[tid] +
                    " | YENIDEN TESLIM: kanit dosyasini yaz + gorev_kutusu teslim ile review'a sok.").strip(" |")
        n += 1
        print("RED:", tid)

with open(P, "w", encoding="utf-8", newline="\n") as f:
    json.dump(tb, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("Guncellenen gorev:", n)
