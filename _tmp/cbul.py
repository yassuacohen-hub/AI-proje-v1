"""Bulgu defteri + salih'e cevap (idempotent)."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
T = "ORCH-KIMLIK-ZINCIRI-01"
ISARET = "D-338 _mesaj_kontrol_et yon filtresi"


def sh(*a):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=180)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


ozet = (
    "DUZELTILDI (D-338): scripts/gorev_kutusu.py _mesaj_kontrol_et() yon "
    "bilgisine bakmiyordu; sadece task_id + yanit_alindi kontrol ediyordu. "
    "SONUC: salih'in ihsan'a GONDERDIGI 3 rapor (ALTYAPI-MIMIR-BAGLAM-01) salih'in "
    "KENDI teslimini blokluyordu - rapor, salih'e sorulan soru degil. Ayrica 11 kayit "
    "kime==kimden (ihsan->ihsan) her teslimi blokluyordu. OLÇÜM: canli veride "
    "ALTYAPI-MIMIR-BAGLAM-01 icin salih'e 10 engel -> duzeltme sonrasi 0 engel. "
    "DÜZELTME: imzaya ajan parametresi eklendi; kime in (ajan,'hepsi') ve "
    "kimden != ajan kirilimi _chat_yeni_mesajlar() ile ayni kaliba getirildi. "
    "KIRMA KANITI: eski kural 3 engel -> yeni 0 (kendi raporlarinla bloklanma "
    "yordu); ihsan->ihsan 1->0; salih'e dogrudan soru + 'hepsi' duyurusu 2->2 "
    "(kapi hala gercek sorulari blokluyor); cevaplanmis mesaj 1->0. REGRESYON: "
    "38 passed, 2 skipped, rc=0. NOT: salih'in 'mesaj tipine bakmiyor' tespiti "
    "yon eksigine isaret ediyordu ama 'type' alani 147 kaydin HEPSINDE bos; ona "
    "gore filtre olu kod olurdu, bu yuzden EKLENMEDI. Ayrica alan adi 'tip' degil "
    "'type'.")

karar = (
    "salih hakliydi: teslim kapisi mesaj tipine/yonune bakmadan her mesaji soru "
    "sayiyordu. Teshis veriden cikti, tahminden degil. Iki duzeltme yapildi: "
    "(1) gorev_kutusu.py:370 _mesaj_kontrol_et(task_id, ajan) - yon kirilimi; "
    "(2) cagri satiri 553 _mesaj_kontrol_et(args.task_id, args.ajan). Duyarli "
    "dosya yazimi hash korumali ve atomik yapildi (sha256 9849e48a -> b4c9889c); "
    "AST parse dogrulandi. Regresyon 38 passed/2 skipped. Kalan risk: "
    "'hepsi' duyurusu hala herkesi bloklar; bu kasitli ama gurultu yaratabilir.")

if ISARET in (O / "bulgu_defteri.md").read_text(encoding="utf-8", errors="replace"):
    print("[1] bulgu zaten var, ATLANDI")
else:
    rc, c = sh("scripts/bulgu_defteri.py", "ekle", "--task-id", T, "--rol", "yasu",
               "--renk", "tamam", "--ozet", ozet, "--karar", karar)
    print(f"[1] bulgu rc={rc} :: {c[:220]}")

sorun = ("DUZELTILDI: gorev_kutusu.py _mesaj_kontrol_et artik YON bakmiyor. "
         "canli veride ALTYAPI-MIMIR-BAGLAM-01 senin icin 10 engel -> 0 engel. "
         "kapi acildi, teslimini tekrarla.")
cozum = ("imza: (task_id, ajan). kirilim: kime in (ajan,'hepsi') + kimden != ajan. "
         "KIRMA KANITI 4/4: kendi raporlarin 3->0, ihsan->ihsan 1->0, sana dogrudan "
         "soru + 'hepsi' duyurusu 2->2 (kapi hala duruyor), cevaplanmis 1->0. "
         "REGRESYON 38 passed 2 skipped rc=0. ONEMLI: 'type' alani 147 kaydin "
         "hepsinde BOS, tip filtresi koymadim (olu kod olurdu) - alan adi 'tip' "
         "degil 'type'. Tespitin yon eksigine isaret ediyordu: teslim kapisi kendi "
         "cikti raporunu soru sayiyordu. dosya 9849e48a -> b4c9889c (hash korumali).")

k = [x for x in (O / "ajan-chat.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
if any("DUZELTILDI: gorev_kutusu.py" in x for x in k):
    print("[2] salih kaydi zaten var, ATLANDI")
else:
    sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
    from company_master import chat
    s = chat.ac(ajan="salih", task_id=T, sorun=sorun, cozum=cozum,
                kimden="yasu", onem="yuksek")
    print(f"[2] salih kaydi: {s['kimden']}->{s['ajan']} [{s['durum']}] onem={s['onem']}")

d = (O / "bulgu_defteri.md").read_text(encoding="utf-8", errors="replace")
print(f"\nDOGRULAMA: ISARET sayisi = {d.count(ISARET)} (1 olmali)")