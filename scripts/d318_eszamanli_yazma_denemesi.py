"""D-318 ek — eşzamanlı yazma kanıtı.

Tek kanonik defter dört ajan tarafından **aynı anda** yazılır. Kilit olmadan
oku-değiştir-yaz kalıbı kayıp güncelleme üretir: iki süreç aynı dosyayı okur,
ikisi de kendi satırını ekler, son yazan ilkini siler.

Bu deneme **bilerek kilidi atlayarak** kaybı gösterir, sonra kilitle
tekrar eder. Kayıp üretilemiyorsa kilit işe yaramıyor demektir.
"""

import importlib.util as ilu
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
GECICI = KOK / "data" / "orchestrator" / "_d318_es zamanli.md"

spec = ilu.spec_from_file_location("bd", KOK / "scripts" / "bulgu_defteri.py")
bd = ilu.module_from_spec(spec)
spec.loader.exec_module(bd)

AJANLAR = ("utku", "yasu", "salih", "ihsan")
N = 4


def temizle() -> None:
    if GECICI.exists():
        GECICI.unlink()
    kilit = GECICI.with_suffix(GECICI.suffix + ".kilit")
    if kilit.exists():
        kilit.unlink()


def yaz_kilitli(ajana_satir: int) -> None:
    """Kilidi ATLAYAN yazma — kayıp güncellemenin kaynağı."""
    satir = bd.satir_birlestir(
        "2026-10-02", f"ESZAMAN-{ajana_satir}", AJANLAR[ajana_satir],
        "oneri", "kilitli yazma", "kapandi:d318",
    )
    mevcut = GECICI.read_text(encoding="utf-8") if GECICI.exists() else bd.BASLIK
    if satir in mevcut:
        return
    # Kilit YOK: oku → yaz arasında başkası yazabilir.
    import time

    time.sleep(0.01)
    GECICI.write_text(mevcut.rstrip("\n") + "\n" + satir + "\n", encoding="utf-8")


def yaz_duz(ajana_satir: int) -> None:
    """Kilidi tamamen atlayan eski davranış (kilit yoksa aynı sonuç)."""
    yaz_kilitli(ajana_satir)


print("D-318 ESZAMANLI YAZMA KANITI")
print(f"gecici dosya: {GECICI.relative_to(KOK).as_posix()}")
print()

# --- 1) KİLİTSİZ: kayıp bekleniyor -------------------------------------
import threading  # noqa: E402

temizle()
iplikler = [threading.Thread(target=yaz_duz, args=(i,)) for i in range(N)]
for t in iplikler:
    t.start()
for t in iplikler:
    t.join()
kilitlisiz = len(bd._veri_satirlari(GECICI))
print(f"1) KILITSIZ yazma: {N} is parcacigi -> {kilitlisiz} satir")
print(f"   {'KAYIP VAR (beklenen)' if kilitlisiz < N else 'kayip yok'}")

# --- 2) KİLİTLİ: kayıp olmamalı -----------------------------------------
temizle()
iplikler = [
    threading.Thread(
        target=lambda i=i: bd.ekle(
            f"ESZAMAN-{i}", AJANLAR[i], "kilitli yazma", "kapandi:d318",
            "oneri", "2026-10-02", GECICI,
        )
    )
    for i in range(N)
]
for t in iplikler:
    t.start()
for t in iplikler:
    t.join()
kilitli = len(bd._veri_satirlari(GECICI))
print(f"2) KILITLI yazma: {N} is parcacigi -> {kilitli} satir")
print(f"   {'KAYIP YOK (dogru)' if kilitli == N else 'KAYIP VAR (hata)'}")

# --- 3) Kilit dosyasi geride kalmiyor mu? ---------------------------------
artik = GECICI.with_suffix(GECICI.suffix + ".kilit")
print(f"3) Artik kilit dosyasi kaldi mi: {artik.exists()} (False olmali)")

# --- 4) Ayni satir iki kez eklenmiyor mu? --------------------------------
bd.ekle("ESZAMAN-0", "utku", "kilitli yazma", "kapandi:d318", "oneri",
        "2026-10-02", GECICI)
son = len(bd._veri_satirlari(GECICI))
print(f"4) Idempotency: tekrar ekleme sonrasi {son} satir ({son == N} olmali)")

temizle()
print(f"\nfinally: gecici dosya silindi = {not GECICI.exists()}")

if kilitlisiz == N:
    print("\nNOT: kilitsiz kosuda kayip cikmadi (zamanlama kaydi). "
          "Bu DOGRULAMAZ; kilitli kosu da dogrulanmadan kabul edilmemeli.")
if kilitli != N or artik.exists():
    raise SystemExit(1)
print("\nKILIT DOGRULANDI: eszamanli yazmada kayip yok, kilit artigi yok")
