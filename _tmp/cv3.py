"""ALTYAPI-ODIN-MASKE-V3-01 ac (V3 maskesizlik gercek acik)."""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
YENI = "ALTYAPI-ODIN-MASKE-V3-01"

v = json.loads((O / "task_board.json").read_text(encoding="utf-8", errors="replace"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
var = next((g for g in gs if g.get("id") == YENI), None)
print(f"gorev zaten var mi: {bool(var)}  ({var.get('durum') if var else '-'})")

if var:
    print("ATLANDI")
    sys.exit(0)

aciklama = (
    "OLCUM: sunum.py maskeleme_odin(metin, hedef='musteri', kaynak='V3') None "
    "donuyor. V3 = musteri endpoint'i (bkz. docs/ODIN_DEPLOYMENT_ARCHITECTURE.md: "
    "musteri_id filtreli DB view arkasinda). Genel maske yalnizca kaynak='maske' "
    "veya ic_kaynak/company_master tespit edildiginde uygulaniyor; V3 hicbiri "
    "tetiklemiyor. SONUC: musteri endpoint'i maskelemesiz calisiyor. K4 olcumu "
    "artik bunu yakaliyor (bf7252f5): kacak_tespit_et(None) -> KAPIDAN_GECMEDI, "
    "bu yuzden odun K4 esiginden gecemez. ANCAK bu yalnizca TEST'te gorunur; "
    "URETIMDE musteriye ic veri sizabilir. IS: V3 yolunda da cikis kapisi "
    "uygula - ya genel maske V3'te de calissin ya da V3 ciktisi zorunlu olarak "
    "maske katmanindan gecsin. KABUL: (a) kacakli V3 cikti canli testte maskeli "
    "donuyor, (b) tests/test_odin_kacak_olcer.py gecer, (c) odun K3/K4 kosulabilir "
    "hale geliyor. BAGIMLILIK: ALTYAPI-ODIN-EGITIM-PIPELINE (utku) - ayni "
    "endpoint'i yaziyor; maske karari orada kesinlesmeli. NOT: ALTYAPI-ODIN-"
    "UYARLAMA-01 done kapandi ama K3/K4 hic kosulmadi; bu acik o duzelmeden kapanmaz."
)

r = subprocess.run(
    [sys.executable, "scripts/gorev_kutusu.py", "ekle",
     "--task-id", YENI, "--baslik", "ODIN musteri endpoint'i (V3) maskelemesiz",
     "--aciklama", aciklama, "--ajan", "utku", "--onem", "yuksek",
     "--bagimlilik", "ALTYAPI-ODIN-EGITIM-PIPELINE"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=300)
print(f"\n[ekle] rc={r.returncode}")
print("  " + ((r.stdout or "") + (r.stderr or "")).strip()[:800].replace("\n", "\n  "))

print()
print("=== DOGRULAMA ===")
v = json.loads((O / "task_board.json").read_text(encoding="utf-8", errors="replace"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == YENI), None)
if g:
    print(f"  id       : {g.get('id')}")
    print(f"  durum    : {g.get('durum')}")
    print(f"  ajan     : {g.get('ajan')}")
    print(f"  onem     : {g.get('onem')}")
    print(f"  bagimlilik: {g.get('bagimlilik')}")
    print(f"  baslik   : {g.get('baslik')}")
else:
    print("  !! GOREV BULUNAMADI")
print(f"  pano toplam gorev: {len(gs)}")