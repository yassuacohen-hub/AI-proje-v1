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
from src.company_master.orchestrator import duzen
from src.company_master.orchestrator import isbirligi


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


def oto_destek():
    """Bosta ajanslara yonelik otomatik destek gorevleri olusturur."""
    olusan = 0
    for ajan in isbirligi.bos_ajanlar():
        oneriler = isbirligi.yardim_edilebilir(ajan, limit=3)
        for oner in oneriler:
            try:
                isbirligi.destek_al(ajan, oner["task_id"], oner["rol"])
                print(f"  DESTEK: [{ajan}] -> {oner['task_id']} ({oner['rol']})")
                olusan += 1
            except ValueError:
                pass
    return olusan


def nobetci_tur():
    """Tek nobetci turu - teslimleri onaylar ve zinciri devam ettirir."""
    duzeltilen = 0

    # 0. Otomatik destek
    if args.oto_destek:
        d = oto_destek()
        duzeltilen += d
        if d:
            print(f"  OTOMATIK DESTEK: {d} gorev olusturuldu")

    # 1. Onay bekleyenleri onayla (S-07: yalniz P2 ve alti; P0/P1 roo elle onaylar)
    kuyruk = trigger.onay_bekleyenler()
    for k in kuyruk:
        try:
            uygun, gerekce = trigger.otomatik_onaylanabilir(k["task_id"])
            if not uygun:
                print(f"  ELLE ONAY GEREKLI: {k['task_id']} -> roo ({gerekce})")
                continue
            trigger.onayla(k["task_id"], "oto-nobetci")
            print(f"  ONAYLANDI: {k['task_id']} (teslim: {k['ajan']})")
            _ses_teslim_onay()
            duzeltilen += 1
        except Exception as e:
            print(f"  HATA: {k['task_id']} - {e}")
    
    # 2. Tetik dosyasindaki teslim edilmis gorevleri kontrol et
    for ajan in duzen.AJANLAR:
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
    
    # 3. Pano hijyeni (sessiz: degisiklik varsa yaz + ses)
    try:
        r = duzen.pano_bakim()
        islem = (r["dedupe"] + r["tetik_esit"] + len(r["zincir"])
                 + len(r["acilan"]) + len(r["kapanan"]))
        if islem:
            print(f"  BAKIM: dedupe={r['dedupe']} tetik={r['tetik_esit']} "
                  f"zincir={len(r['zincir'])} blokaj_ac={len(r['acilan'])}")
            duzeltilen += islem
    except Exception:
        pass

    return duzeltilen


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Otomatik nobetci")
    parser.add_argument("--surekli", action="store_true", help="Surekli calistir")
    parser.add_argument("--aralik", type=int, default=60, help="Surekli calisma araligi (saniye)")
    parser.add_argument("--test-ses", action="store_true", help="Ses testi calistir")
    parser.add_argument("--oto-destek", action="store_true",
                        help="Bosta ajanslara otomatik destek gorevleri olustur")
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
