"""COMMIT: yalnizca scripts/gorev_kutusu.py (chat_gonder.py KAHIN'in, dokunulmaz)."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(*a, timeout=900):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


rc, c = git("add", "--", "scripts/gorev_kutusu.py")
print(f"[add] rc={rc} {c[:100]}")

rc, staged = git("diff", "--cached", "--stat")
print(f"\n[staged]\n  " + (staged or "(bos)").replace("\n", "\n  "))
print(f"\n  .py dosya sayisi = {staged.count('.py')} (1 beklenir)")

if "gorev_kutusu.py" not in staged or staged.count(".py") != 1:
    print("!! beklenmedik staged icerik -> COMMIT ATLANDI")
    sys.exit(1)

mesaj = (
    "fix(gorev_kutusu): teslim kapisi mesaj yonune ve turunu bakmiyordu (D-338)\n\n"
    "_mesaj_kontrol_et() yalnizca task_id + yanit_alindi kontrol ediyordu. KIMDEN\n"
    "gelip KIME gittigine ve ne tur olduguna hic bakmiyordu; sonuc olarak salih'in\n"
    "ihsan'a gonderdigi raporlar salih'in KENDI teslimini blokluyordu. Canli veri\n"
    "olcumu: ALTYAPI-MIMIR-BAGLAM-01 icin salih'e 10 engel.\n\n"
    "Iki katmanli bloklama kurali (geriye donuk uyumlu):\n"
    "  1) yon - kime in (ajan,'hepsi') ve kimden != ajan\n"
    "            (_chat_yeni_mesajlar ile ayni kalip)\n"
    "  2) tur - chat_gonder.py'nin yazdigi alanlar:\n"
    "            mahiyet='teslim_bloklayici' bloklar, 'bilgi' bloklamaz\n"
    "            tur='bilgi' (--rapor) bloklamaz\n"
    "            alanlar yoksa (147 eski kayit) yon kuralina dusulur\n\n"
    "Kirma kaniti 6/6: kendi raporlari 3->0, --blok sorusu 2->2 (kapi duruyor),\n"
    "baska ajana soru 1/0, cevaplanmis 1->0, ihsan->ihsan 1->0, alan yokken yon\n"
    "kurali devrede. Regresyon: 38 passed, 2 skipped."
)
rc, c = git("commit", "-m", mesaj)
print(f"\n[commit] rc={rc}")
print("  " + c.replace("\n", "\n  ")[:1500])

rc, c = git("show", "--stat", "HEAD")
print(f"\n[HEAD] {c[:600]}")

rc, c = git("status", "--short", "--", "scripts/chat_gonder.py")
print(f"\n[chat_gonder.py hala unstaged mi?] {c!r}")