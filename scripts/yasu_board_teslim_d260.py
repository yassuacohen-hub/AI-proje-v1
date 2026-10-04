"""YASU: VERI-SEMA-DOGRULA-02 ve -03 panoyu teslim (review) durumuna alir."""
import json
import pathlib
from datetime import datetime

P = pathlib.Path(__file__).resolve().parents[1] / "data/orchestrator/task_board.json"
d = json.loads(P.read_text(encoding="utf-8-sig"))
ts = d if isinstance(d, list) else d.get("gorevler", d.get("tasks", []))

notlar = {
    "VERI-SEMA-DOGRULA-02":
        "entity_matches: 1 dosyada 2 SELECT (threshold_optimizer.py:31,44), "
        "INSERT YOK. api_usage_daily: 1 dosyada 3 SELECT "
        "(admin_kpi.py:108,115,313), INSERT YOK. Canli olcum: ikisi de tablo VAR, "
        "satir 0. Rapor: plans/rapor_yasu_VERI-SEMA-DOGRULA-02.md",
    "VERI-SEMA-DOGRULA-03":
        "Brief varsayimi YANLIS: nace_codes CREATE TABLE 0002_relations.sql'de, "
        "0006 sadece companies ALTER. Canli: 6 sutun, dil sutunu YOK. "
        "sunum.py:acilim_getir() 1 parametre, lang YOK, SELECT title. "
        "title verisi Ingilizce (docstring 'Turkce' diyor - D-260 ihlali). "
        "nace_codes 3319 satir, title bos 0, orphan 0. "
        "Rapor: plans/rapor_yasu_VERI-SEMA-DOGRULA-03.md",
}

bitis = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
gun = 0
for t in ts:
    tid = str(t.get("task_id") or "")
    if tid in notlar:
        t["durum"] = "review"
        t["not"] = notlar[tid]
        t["bitis"] = bitis
        gun += 1
        print(f"{tid} -> review")

P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
             encoding="utf-8")
print(f"guncellenen: {gun}")
