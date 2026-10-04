"""Onemli durum + OLASI SONUCLAR chate (D-336 gonderen)."""
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
from company_master import chat  # noqa: E402

k = (KOK / "data" / "orchestrator" / "ajan-chat.jsonl").read_text(
    encoding="utf-8", errors="replace")
if "BLOKE: SCRAPE-004 teslimi" in k:
    print("zaten var, ATLANDI")
    sys.exit(0)

s = chat.ac(
    ajan="ihsan",
    task_id="SCRAPE-004-QWEN-SINIFLANDIRMA",
    sorun=("BLOKE: SCRAPE-004 teslimi regresyon belirsizligi nedeniyle bekliyor. "
           "pano 'devam' da kalmisti; kanit kodu c63e55a4'te commit'liydi."),
    cozum=("KESIN OLCULEN: 6/6 kabul maddesi kanitli; p95 22.7ms (esik 2000); V3 kapisi "
           "etiket YAZMIYOR. riskli nokta: _anahtar_bir onbellegi commit'li DEGIL, "
           "is agacinda duruyor - onceki turda commitlenmemis is kaybolmustu."),
    kimden="yasu", onem="yuksek")
print(f"1) {s['kimden']}->{s['ajan']} [{s['durum']}]")

s2 = chat.ac(
    ajan="ihsan",
    task_id="SCRAPE-004-QWEN-SINIFLANDIRMA",
    sorun=("OLASI SONUCLAR (regresyon bitince karar verilecek): A) yesilse -> "
           "commit + teslim. B) canli-test kirilganligi -> canli isaretle, sonra "
           "commit + teslim."),
    cozum=("C) gercek kod hatasi -> commit geri alinir, once duzeltilir. D) sonuc "
           "belirsiz kalirsa hicbir sey yapilmaz, olcum araci duzeltilir. Bu turda "
           "5 kez yanlis teshis kurdum (kanca yok, V3 acik, kimlik hatasi) - hepsi "
           "olcum atlamadan; bu yuzden belirsizlikte TAHMIN YURUTMEYIM."),
    kimden="yasu", onem="yuksek")
print(f"2) {s2['kimden']}->{s2['ajan']} [{s2['durum']}]")

import json
sat = [json.loads(x) for x in
       (KOK / "data" / "orchestrator" / "ajan-chat.jsonl").read_text(
           encoding="utf-8", errors="replace").splitlines() if x.strip()]
print(f"\nDOGRULAMA: acik kayitlarim = "
      f"{sum(1 for r in sat if r.get('kimden')=='yasu' and r.get('durum')=='acik')}")