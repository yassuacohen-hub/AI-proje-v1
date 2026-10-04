"""D-318 mandal kırma denemesi — teslim kapısı gerçekten çalışıyor mu?

Mandal (D-244): kapıyı kır; kırmadan yeşil görmek anlamsızdır.

Kırılan iki nokta:
  1. Var olmayan görev kimliği → kapı reddetmeli (dosyaya yazmadan önce).
  2. `bulgu.task_var_mi` sahte `True` → kapı geçmeli (kapının yalnız
     reddettiğini değil, **doğru bulunca da geçirdiğini** kanıtlar).

Yan etki: görev kuyruğu/panoya dokunulmaz; `bulgu_defteri.py` fonksiyonları
geçici dosyaya yazılır ve finally ile temizlenir.
"""

import importlib.util as ilu
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
TMP = KOK / "data" / "orchestrator" / "_d318_mandal_defteri.md"

spec = ilu.spec_from_file_location("bd", KOK / "scripts" / "bulgu_defteri.py")
bd = ilu.module_from_spec(spec)
spec.loader.exec_module(bd)

hata = 0


def yaz(etiket: str, gecti: bool) -> None:
    global hata
    print(f"  [{'GECTI' if gecti else 'KALDI'}] {etiket}")
    if not gecti:
        hata += 1


print("D-318 BULGU KAPISI MANDAL KIRMA DENEMESI")
print(f"gecici defter: {TMP.relative_to(KOK).as_posix()}")
print()

try:
    # --- 1) Kapı, defterde olmayan görevi reddetmeli -------------------
    print("1) BOS DEFTER — kapı reddetmeli")
    TMP.write_text(bd.BASLIK, encoding="utf-8")
    yaz("olmayan görev reddedildi", not bd.task_var_mi("D-318-MANDAL-YOK", TMP))

    # --- 2) Satır yazıldıktan sonra kapı geçmeli ---------------------
    print("2) SATIR YAZILDI — kapı geçmeli")
    bd.ekle(
        "D-318-MANDAL-YOK", "utku",
        "mandal bulgusu", "kapandi:tests/test_tsg_zincir.py", "oneri",
        dosya=TMP,
    )
    yaz("yazilan gorev bulundu", bd.task_var_mi("D-318-MANDAL-YOK", TMP))

    # --- 3) Idempotency: ayni satir iki kez eklenmez ------------------
    print("3) IDEMPOTENCY — ayni satir iki kez eklenmez")
    once = TMP.read_text(encoding="utf-8").count("D-318-MANDAL-YOK")
    bd.ekle(
        "D-318-MANDAL-YOK", "utku",
        "mandal bulgusu", "kapandi:tests/test_tsg_zincir.py", "oneri",
        dosya=TMP,
    )
    twice = TMP.read_text(encoding="utf-8").count("D-318-MANDAL-YOK")
    yaz(f"1 -> {twice} (degismedi)", once == twice == 1)

    # --- 4) Kanonik disiplini: bozuk alan reddedilmeli ---------------
    print("4) KANONIK ALAN — bozuk giris reddedilmeli")
    try:
        bd.ekle("X", "bilinmeyen-rol", "ozet", "karar", "oneri", dosya=TMP)
        yaz("kanonik olmayan rol reddedildi", False)
    except ValueError:
        yaz("kanonik olmayan rol reddedildi", True)

    try:
        bd.ekle("X", "utku", "ozet", "karar", "pembe", dosya=TMP)
        yaz("gecersiz renk reddedildi", False)
    except ValueError:
        yaz("gecersiz renk reddedildi", True)

    # --- 5) Karar alani bos birakilamaz ------------------------------
    print("5) KARAR ALANI — bos birakilamaz")
    try:
        bd.satir_birlestir("2026-10-02", "X", "utku", "oneri", "ozet", "  ")
        yaz("bos karar alani reddedildi", False)
    except ValueError:
        yaz("bos karar alani reddedildi", True)

    # --- 6) Baslik metni veri sanilmamali ----------------------------
    print("6) AYIRICI — baslik paragrafi veri sayilmamali")
    yaz(f"veri satiri = {len(bd._veri_satirlari(TMP))} (1 beklenir)",
       len(bd._veri_satirlari(TMP)) == 1)

    # --- 7) Islenmemis satir tespiti ----------------------------------
    print("7) DENETIM — islenmemis satir yakalanir")
    TMP.write_text(
        bd.BASLIK + "\n2026-10-02 | G1 | utku | oneri | ozet | \n",
        encoding="utf-8",
    )
    yaz(f"islenmemis = {len(bd.islenmemis(TMP))} (1 beklenir)",
       len(bd.islenmemis(TMP)) == 1)

finally:
    # --- finally ile yeşile dön ---------------------------------------
    if TMP.exists():
        TMP.unlink()
    print(f"\nfinally: gecici defter silindi = {not TMP.exists()}")

print()
if hata:
    print(f"MANDAL BASARISIZ: {hata} kontrol kalmadi")
    raise SystemExit(1)
print("MANDAL BASARILI: tum kontroller gecti")
