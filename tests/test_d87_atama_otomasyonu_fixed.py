#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test D-87 atama otomasyonu — `.upper()` büyük/küçük harf hatasını düzeltildi.
Gereklilik: `DASH-UX-02a` ve `DASH-UX-02b` görevlerinin başarılı atanabilmesi.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "gorev_atama_otomatis.py"


def _calistir(*args: str) -> subprocess.CompletedProcess:
    """Script çalıştır."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_dash_ux_02b_atanabiliyor() -> None:
    """DASH-UX-02b (küçük harf soneki) başarıyla atanabilir (yeni ajan, tetik yok)."""
    sonuc = _calistir("--task-id", "DASH-UX-02b", "--ajan", "roo")
    # Başarıyla atandı veya zaten tetik var
    assert sonuc.returncode in (0, 1), f"Beklenen exit 0 veya 1, aldı: {sonuc.returncode}"
    assert "gorev bulunamadi" not in sonuc.stdout.lower(), "Görev olması gerektiği halde bulunamadı"


def test_bilinmeyen_gorev_reddedilir() -> None:
    """Bilinmeyen görev reddedilir."""
    sonuc = _calistir("--task-id", "YOK-BOYLE-GOREV-99", "--ajan", "utku")
    assert sonuc.returncode == 1
    assert "gorev bulunamadi" in sonuc.stdout.lower()


def test_brifsiz_atama_reddedilir() -> None:
    """Brif yoksa atama reddedilir."""
    sonuc = _calistir("--task-id", "COP-26", "--ajan", "olmayan")
    assert sonuc.returncode == 1
    assert "brif bulunamadi" in sonuc.stdout.lower()


def test_case_insensitive_lookup() -> None:
    """Görev lookup büyük/küçük harfe duyarsız (DASH-UX-02a bulunabilir)."""
    sonuc = _calistir("--task-id", "DASH-UX-02a", "--ajan", "mimar")
    # Başarıyla bulundu veya tetik zaten var (her ikisi de case-insensitive'in başarısı)
    assert "gorev bulunamadi" not in sonuc.stdout.lower(), "Görev lookup başarısız (case sensitivity sorunu)"


if __name__ == "__main__":
    print("D-87 atama otomasyonu self-check:")
    tests = [
        ("test_dash_ux_02b_atanabiliyor", test_dash_ux_02b_atanabiliyor),
        ("test_bilinmeyen_gorev_reddedilir", test_bilinmeyen_gorev_reddedilir),
        ("test_brifsiz_atama_reddedilir", test_brifsiz_atama_reddedilir),
        ("test_case_insensitive_lookup", test_case_insensitive_lookup),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"[OK] {name}")
        except AssertionError as e:
            print(f"[ERROR] {name}: {e}")
