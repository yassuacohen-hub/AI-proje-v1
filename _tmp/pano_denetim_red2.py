# -*- coding: utf-8 -*-
"""D-357 denetim reddi 2: kanitsiz/uncommitted done gorevlerini aktife cek."""
import json, io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"Huginn Data Insights/data/orchestrator/task_board.json"
with open(P, encoding="utf-8") as f:
    tb = json.load(f)

SEBEB = {
    "VERI-RAPIDAPI-OSINT-ISTEMCI-01": "CANLI AGACTA YOK: engine/rapidapi_osint.py + testi eksik; eski kopya _ARSIV'e suruklenmis. Done=commit+kanit (D-357).",
    "VERI-MUSTERI-ODEME-AYAR-01": "CANLI AGACTA YOK: web_dashboard/tabs/musteri_odeme.py + test yok; kopyalar _ARSIV'de (commitlenmemis, temizlik suruklemis).",
    "VERI-OSB-MASTER-LISTE-01": "GOC 0060=mersis_tobb_data (osb degil); test_osb_master.py yalniz _ARSIV'de. Canli kanit yok.",
    "API-V1-NETWORK-REPORT-01": "CANLI AGACTA YOK: v1_network.py + testi yok (yalniz _ARSIV kopyasi).",
    "UI-ADMIN-PANEL-DENETIM-ALTYAPI": "test_admin_denetim.py canli degil (yalniz _ARSIV) - commit eksik (D-357).",
    "UI-PAKET-ROZET-01": "test_paket_rozet.py canli degil (yalniz _ARSIV) - commit eksik (D-357).",
    "VERI-OZELLIK-MATRISI-SIM-01": "paket_simulasyon.py canli degil; test_ozellik_matrisi.py hic yok - yeniden teslim: canli yol + commit + kanit.",
}
simdi = datetime.datetime.now().isoformat(timespec="seconds")
n = 0
for t in tb:
    tid = t.get("id")
    if tid in SEBEB and (t.get("durum") or "").lower() == "done":
        t["durum"] = "aktif"
        t["bitis"] = None
        t["not"] = (str(t.get("not") or "") + " | IHSAN DENETIM REDDI " + simdi +
                    " (D-357): " + SEBEB[tid] +
                    " | YENIDEN TESLIM: dosyayi CANLI agaca yaz + git commit + kanit alani + gorev_kutusu teslim.").strip(" |")
        n += 1
        print("RED:", tid, "(", t.get("sahip"), ")")

with open(P, "w", encoding="utf-8", newline="\n") as f:
    json.dump(tb, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("Guncellenen gorev:", n)
