# -*- coding: utf-8 -*-
"""Otomatik nobetci - teslimleri onaylar ve zinciri devam ettirir.

Kullanim:
    python scripts/oto_nobetci.py          # Tek seferlik calistir
    python scripts/oto_nobetci.py --surekli  # Her 60 saniyede bir calistir
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.company_master.orchestrator import trigger


def _ses_cal(frekans=600, sure=200, tekrar=2):
    """Windows'ta komik bir ses cal."""
    try:
        import winsound
        for _ in range(tekrar):
            winsound.Beep(frekans, sure)
            winsound.Beep(frekans + 200, sure)
    except Exception:
        pass


def _ses_zincir_devam():
    """Zincir devaminda komik melodi."""
    try:
        import winsound
        # Yukselen melodi - isler yolunda
        winsound.Beep(523, 150)  # Do
        winsound.Beep(659, 150)  # Mi
        winsound.Beep(784, 200)  # Sol
        winsound.Beep(1047, 300) # Do (yuksek)
    except Exception:
        pass


def _ses_teslim_onay():
    """Teslim onayi sesi."""
    try:
        import winsound
        # Kisa, oz bir bip
        winsound.Beep(880, 100)
        winsound.Beep(1100, 150)
    except Exception:
        pass


def nobetci_tur():
    """Tek nobetci turu - teslimleri onaylar ve zinciri devam ettirir."""
    duzeltilen = 0
    
    # 1. Onay bekleyenleri onayla
    kuyruk = trigger.onay_bekleyenler()
    for k in kuyruk:
        try:
            trigger.onayla(k["task_id"], "oto-nobetci")
            print(f"  ONAYLANDI: {k['task_id']} (teslim: {k['ajan']})")
            _ses_teslim_onay()
            duzeltilen += 1
        except Exception as e:
            print(f"  HATA: {k['task_id']} - {e}")
    
    # 2. Tetik dosyasindaki teslim edilmis gorevleri kontrol et
    for ajan in ["kilo", "roo", "cline", "orkestrator"]:
        try:
            tum = trigger._tetikleri_oku(ajan)
            teslim = [k for k in tum if k.get("durum") == "teslim"]
            for t in teslim:
                sonraki = trigger.zincir_devam_et(t["task_id"], ajan)
                if sonraki:
                    print(f"  ZINCIR: [{ajan}] {t['task_id']} -> {sonraki['task_id']}")
                    _ses_zincir_devam()
                    duzeltilen += 1
        except Exception:
            pass
    
    return duzeltilen


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Otomatik nobetci")
    parser.add_argument("--surekli", action="store_true", help="Surekli calistir")
    parser.add_argument("--aralik", type=int, default=60, help="Surekli calisma araligi (saniye)")
    parser.add_argument("--test-ses", action="store_true", help="Ses testi calistir")
    args = parser.parse_args()
    
    if args.test_ses:
        print("Test: Zincir devam sesi...")
        _ses_zincir_devam()
        time.sleep(1)
        print("Test: Teslim onay sesi...")
        _ses_teslim_onay()
        return
    
    if args.surekli:
        print(f"[OTO-NOBETCI] Surekli mod baslatildi (aralik: {args.aralik}s)")
        print("  Durdurmak icin Ctrl+C basin\n")
        try:
            while True:
                duzeltilen = nobetci_tur()
                if duzeltilen > 0:
                    print(f"  Toplam: {duzeltilen} islem\n")
                time.sleep(args.aralik)
        except KeyboardInterrupt:
            print("\n[OTO-NOBETCI] Durduruldu")
    else:
        duzeltilen = nobetci_tur()
        if duzeltilen == 0:
            print("(düzeltilecek bir şey yok)")
        else:
            print(f"\nToplam: {duzeltilen} işlem")


if __name__ == "__main__":
    main()
