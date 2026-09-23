# -*- coding: utf-8 -*-
"""ALTYAPI-MOJIBAKE-DIZIN-01 testleri: --dizin taramasi + kuru calisma guvencesi.

Kaynak ASCII tutulur (mojibake ornekleri \\u escape ile uretilir) — test
dosyasinin kendisi bozuk karakter tasiyarak kendi Dogrulugunu kaybetmesin.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
SCRIPT = KOK / "scripts" / "mojibake_onar.py"

# cp1252 gorunumlu bozuk ornekler (unicode escape ile uretilir):
# "Ba\u00c4\u00b1k" = "Ba\u0131k" (başlık) ikiz gorunumu
# "\u00c3\u00a7\u00c3\u00b6z\u00c3\u00bc\u00c3\u00bc m" = cp1252'de "çözüüm" izi
BOZUK = (
    "# Ba\u00c4\u00b1k\n"
    "Bu sat\u00c3\u00bcrda mojibake var: \u00c3\u00a7\u00c3\u00b6z\u00c3\u00bc\u00c3\u00bc m yok\n"
)
# MOJIBAKE_RX'in eslesdigi tipik iz karakterleri (onarim sonrasi KALMAMALI):
IZ1 = "\u00c3\u00a7"   # Ã§
IZ2 = "\u00c4\u00b1"   # Ä±


def _calistir(*argler: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(SCRIPT), *argler],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(KOK),
    )


def test_dizin_taramasi_bozuk_dosyayi_bulur(tmp_path):
    (tmp_path / "alt").mkdir()
    bozuk = tmp_path / "alt" / "bozuk.md"
    bozuk.write_text(BOZUK, encoding="utf-8")
    sonuc = _calistir("--dizin", str(tmp_path))
    assert sonuc.returncode == 0
    assert "taranan=1" in sonuc.stdout
    assert "degisen=2" in sonuc.stdout


def test_uygula_olmadan_disk_degismez(tmp_path):
    bozuk = tmp_path / "bozuk.md"
    bozuk.write_text(BOZUK, encoding="utf-8")
    onceki = bozuk.read_text(encoding="utf-8")
    sonuc = _calistir("--dizin", str(tmp_path))  # --uygula YOK
    assert sonuc.returncode == 0
    assert bozuk.read_text(encoding="utf-8") == onceki  # DEGISMEDI


def test_uygula_ile_yazar(tmp_path):
    bozuk = tmp_path / "bozuk.md"
    bozuk.write_text(BOZUK, encoding="utf-8")
    sonuc = _calistir("--dizin", str(tmp_path), "--uygula")
    assert sonuc.returncode == 0
    icerik = bozuk.read_text(encoding="utf-8")
    assert IZ1 not in icerik and IZ2 not in icerik  # cp1252 izleri temizlendi


def test_dizin_ve_dosya_birbirini_dislar(tmp_path):
    hedef = tmp_path / "x.md"
    hedef.write_text("temiz\n", encoding="utf-8")
    sonuc = _calistir("--dizin", str(tmp_path), str(hedef))
    assert sonuc.returncode == 2  # argparse error


def test_ozet_satiri_bos_dizinde_cikar(tmp_path):
    sonuc = _calistir("--dizin", str(tmp_path))
    assert sonuc.returncode == 0
    assert "taranan=0 degisen=0" in sonuc.stdout


def test_tek_dosya_geri_uyum_yazmaya_devam(tmp_path):
    """D-48: eski tek-dosya cagirimi (argumansiz mod) yazmaya devam eder."""
    bozuk = tmp_path / "bozuk.md"
    bozuk.write_text(BOZUK, encoding="utf-8")
    sonuc = _calistir(str(bozuk))
    assert sonuc.returncode == 0
    icerik = bozuk.read_text(encoding="utf-8")
    assert IZ1 not in icerik  # eski davranis: yazar


def test_kontrol_yazmaz(tmp_path):
    """Eski --kontrol davranisi korunur: yalniz rapor, yazma yok."""
    bozuk = tmp_path / "bozuk.md"
    bozuk.write_text(BOZUK, encoding="utf-8")
    onceki = bozuk.read_text(encoding="utf-8")
    sonuc = _calistir(str(bozuk), "--kontrol")
    assert sonuc.returncode in (0, 1)
    assert bozuk.read_text(encoding="utf-8") == onceki

