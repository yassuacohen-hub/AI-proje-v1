# -*- coding: utf-8 -*-
"""ORCH-08 — Ajan posta kutusu + kontrolör onay komutu.

AJAN tarafı (oturum başında çalıştır):
    python scripts/gorev_kutusu.py bak --ajan kilo          # bekleyen işler
    python scripts/gorev_kutusu.py al --ajan kilo --task-id X
    python scripts/gorev_kutusu.py teslim --ajan kilo --task-id X --ozet "..."

KONTROLÖR tarafı (orkestratör; onaysız done geçersizdir):
    python scripts/gorev_kutusu.py onay-bekleyen
    python scripts/gorev_kutusu.py onayla --task-id X --ben orkestrator
    python scripts/gorev_kutusu.py reddet --task-id X --ben orkestrator --neden "..."
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Windows konsolu (cp1254) Unicode ok/emoji karakterlerinde cokuyordu.
# Cikti akislarini UTF-8'e cevir; desteklenmeyen karakterlerde cokme yerine degistir.
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - eski Python / yonlendirilmis akis
        pass

from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402


def _ayristir_liste(deger: str | None) -> list[str]:
    if not deger:
        return []
    return [p.strip() for p in deger.split(",") if p.strip()]


def _hata(exc: Exception) -> int:
    print(f"HATA: {exc}", file=sys.stderr)
    return 1


def cmd_bak(args: argparse.Namespace) -> int:
    bekleyen = trigger.bekleyen_tetikler(args.ajan)
    if not bekleyen:
        print(f"[{args.ajan}] posta kutusu bos.")
        return 0
    alarm_yol = tb.STATE_DIR / "triggers" / f"{args.ajan}.ALARM.json"
    alarm = []
    if alarm_yol.exists():
        try:
            alarm = json.loads(alarm_yol.read_text(encoding="utf-8-sig"))
            alarm = alarm if isinstance(alarm, list) else [alarm]
        except (json.JSONDecodeError, ValueError):
            alarm = []
    uyarilar = {a.get("task_id"): a for a in alarm}
    print(f"[{args.ajan}] {len(bekleyen)} bekleyen gorev:")
    for k in bekleyen:
        gorev = tb.gorev_getir(k["task_id"]) or {}
        print(f"\n  {k['task_id']}  ({gorev.get('oncelik', '?')})  tetik: {k['tarih']}")
        print(f"  {gorev.get('baslik', '(pano basligi yok)')}")
        if k.get("uyari_tarihi"):
            a = uyarilar.get(k["task_id"], {})
            print(f"  ⚠️ UYARI ({k.get('uyari_sayisi', '?')}x) — tetik {a.get('uyari_tarihi', k['uyari_tarihi'])}'da firlatilmisti")
        if k.get("talimat"):
            print(f"  TALIMAT: {k['talimat']}")
        if gorev.get("dosyalar"):
            print(f"  KILITLI DOSYALAR: {', '.join(gorev['dosyalar'])}")
        print(f"  -> al: python scripts/gorev_kutusu.py al --ajan {args.ajan} --task-id {k['task_id']}")
    return 0


def cmd_al(args: argparse.Namespace) -> int:
    try:
        sonuc = trigger.tetik_al(args.ajan, args.task_id)
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"ALINDI: {sonuc['task_id']} -> {args.ajan} (durum: aktif)")
    return 0


def cmd_teslim(args: argparse.Namespace) -> int:
    try:
        sonuc = trigger.teslim_et(
            args.task_id, args.ajan, args.ozet, _ayristir_liste(args.cikti)
        )
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"TESLIM: {sonuc['task_id']} -> durum: review (onay bekliyor)")
    print("       Onaysiz done OLMAZ; kontrolor onayi sonrasi tamamlanir.")
    return 0


def cmd_onay_bekleyen(args: argparse.Namespace) -> int:
    kuyruk = trigger.onay_bekleyenler()
    if not kuyruk:
        print("Onay kuyrugu bos.")
        return 0
    print(f"{len(kuyruk)} teslim kontrol bekliyor:")
    for k in kuyruk:
        print(f"\n  {k['task_id']}  <- {k['ajan']}  ({k['teslim_tarihi']})")
        print(f"  OZET: {k['ozet']}")
        if k.get("ciktilar"):
            print(f"  CIKTILAR: {', '.join(k['ciktilar'])}")
        print(f"  -> python scripts/gorev_kutusu.py onayla --task-id {k['task_id']} --ben orkestrator")
    return 0


def cmd_onayla(args: argparse.Namespace) -> int:
    try:
        trigger.onayla(args.task_id, args.ben)
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"ONAYLANDI: {args.task_id} -> done (kilitler otomatik dustu)")
    return 0


def cmd_reddet(args: argparse.Namespace) -> int:
    try:
        trigger.reddet(args.task_id, args.ben, args.neden)
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"REDDEDILDI: {args.task_id} -> aktif (ajan duzeltmeye devam edecek)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ajan posta kutusu + onay (ORCH-08)")
    alt = parser.add_subparsers(dest="komut", required=True)

    def ajanli(p: argparse.ArgumentParser) -> None:
        p.add_argument("--ajan", required=True)

    p = alt.add_parser("bak", help="Bekleyen görevlerini listele"); ajanli(p)
    p.set_defaults(func=cmd_bak)
    p = alt.add_parser("al", help="Görevi al (aktif yap)"); ajanli(p)
    p.add_argument("--task-id", required=True); p.set_defaults(func=cmd_al)
    p = alt.add_parser("teslim", help="İşi teslim et (review'a düşer)"); ajanli(p)
    p.add_argument("--task-id", required=True); p.add_argument("--ozet", required=True)
    p.add_argument("--cikti", default=None, help="Virgülle ayrılı çıktı dosyaları")
    p.set_defaults(func=cmd_teslim)
    p = alt.add_parser("onay-bekleyen", help="Onay bekleyen teslimleri listele")
    p.set_defaults(func=cmd_onay_bekleyen)
    p = alt.add_parser("onayla", help="Teslimi onayla (done)")
    p.add_argument("--task-id", required=True); p.add_argument("--ben", required=True)
    p.set_defaults(func=cmd_onayla)
    p = alt.add_parser("reddet", help="Teslimi reddet (aktife geri)")
    p.add_argument("--task-id", required=True); p.add_argument("--ben", required=True)
    p.add_argument("--neden", required=True); p.set_defaults(func=cmd_reddet)

    
def cmd_zincir(args: argparse.Namespace) -> int:
    """Görev zinciri oluştur (örn. P7-23 → P7-4 → ...)."""
    try:
        task_list = [tid.strip() for tid in args.task_ids.split(",")]
        sonuc = trigger.gorev_zinciri(task_list, args.ajan, args.talimat)
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"ZİNCİR OLUŞTURULDU: {len(task_list)} görev ({args.ajan})")
    print(f"  İlk: {task_list[0]} → hemen tetiklendi")
    if len(task_list) > 1:
        print(f"  Sonraki: {', '.join(task_list[1:])} → zincir_bekleme")
        print(f"  (Her görev tamamlanınca sonraki otomatik tetiklenir)")
    return 0


def cmd_hepsini_tamamla(args: argparse.Namespace) -> int:
    """Tum teslim edilen gorevleri onayla ve zinciri devam ettir."""
    duzeltilen = 0
    
    # 1. Onay bekleyenleri onayla
    kuyruk = trigger.onay_bekleyenler()
    for k in kuyruk:
        try:
            trigger.onayla(k["task_id"], "oto-nobetci")
            print(f"  ONAYLANDI: {k['task_id']} (teslim: {k['ajan']})")
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
                    duzeltilen += 1
        except Exception:
            pass
    
    if duzeltilen == 0:
        print("  (düzeltilecek bir şey yok)")
    else:
        print(f"\n  Toplam: {duzeltilen} işlem")
    
    return 0


def cmd_hepsini_tamamla(args: argparse.Namespace) -> int:
    """Tum teslim edilen gorevleri onayla ve zinciri devam ettir."""
    duzeltilen = 0
    kuyruk = trigger.onay_bekleyenler()
    for k in kuyruk:
        try:
            trigger.onayla(k["task_id"], "oto-nobetci")
            print(f"  ONAYLANDI: {k['task_id']} (teslim: {k['ajan']})")
            duzeltilen += 1
        except Exception as e:
            print(f"  HATA: {k['task_id']} - {e}")
    
    for ajan in ["kilo", "roo", "cline", "orkestrator"]:
        try:
            tum = trigger._tetikleri_oku(ajan)
            teslim = [k for k in tum if k.get("durum") == "teslim"]
            for t in teslim:
                sonraki = trigger.zincir_devam_et(t["task_id"], ajan)
                if sonraki:
                    print(f"  ZINCIR: [{ajan}] {t['task_id']} -> {sonraki['task_id']}")
                    duzeltilen += 1
        except Exception:
            pass
    
    if duzeltilen == 0:
        print("  (düzeltilecek bir şey yok)")
    else:
        print(f"\n  Toplam: {duzeltilen} işlem")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ORCH-08 — Ajan posta kutusu + kontrolör onay")

    sub = parser.add_subparsers(dest="komut", required=True)
    
    bak_p = sub.add_parser("bak", help="Ajanın posta kutusunu göster")
    bak_p.add_argument("--ajan", required=True, help="Ajan adı (kilo, roo, vs.)")
    bak_p.set_defaults(func=cmd_bak)

    al_p = sub.add_parser("al", help="Tetiği al (görevi aktif yap)")
    al_p.add_argument("--ajan", required=True)
    al_p.add_argument("--task-id", required=True)
    al_p.set_defaults(func=cmd_al)

    teslim_p = sub.add_parser("teslim", help="Görevi teslim et (review)")
    teslim_p.add_argument("--ajan", required=True)
    teslim_p.add_argument("--task-id", required=True)
    teslim_p.add_argument("--ozet", required=True, help="Ne yapıldı?")
    teslim_p.add_argument("--cikti", help="Virgülle ayrılmış çıktı dosyaları")
    teslim_p.set_defaults(func=cmd_teslim)

    zincir_p = sub.add_parser("zincir", help="Görev zinciri oluştur")
    zincir_p.add_argument("--ajan", required=True)
    zincir_p.add_argument("--task-ids", required=True, help="Virgülle ayrılmış görev ID'leri (P7-23,P7-4)")
    zincir_p.add_argument("--talimat", default="", help="Tüm görevler için ortak talimat")
    zincir_p.set_defaults(func=cmd_zincir)

    onay_bekleyen_p = sub.add_parser("onay-bekleyen", help="Onay bekleyen teslimleri listele")
    onay_bekleyen_p.set_defaults(func=cmd_onay_bekleyen)

    onayla_p = sub.add_parser("onayla", help="Teslimi onayla (done)")
    onayla_p.add_argument("--task-id", required=True)
    onayla_p.add_argument("--ben", required=True, help="Onaylayan adı (örn. orkestrator)")
    onayla_p.set_defaults(func=cmd_onayla)

    reddet_p = sub.add_parser("reddet", help="Teslimi reddet (aktife geri)")
    reddet_p.add_argument("--task-id", required=True)
    reddet_p.add_argument("--ben", required=True)
    reddet_p.add_argument("--neden", required=True, help="Reddetme nedeni")
    reddet_p.set_defaults(func=cmd_reddet)

    hepsini_tamamla_p = sub.add_parser("hepsini-tamamla", help="Tum teslimleri onayla + zincir devami")
    hepsini_tamamla_p.set_defaults(func=cmd_hepsini_tamamla)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

def cmd_hepsini_tamamla(args: argparse.Namespace) -> int:
    """Tum teslim edilen gorevleri onayla ve zinciri devam ettir."""
    duzeltilen = 0
    
    # 1. Onay bekleyenleri onayla
    kuyruk = trigger.onay_bekleyenler()
    for k in kuyruk:
        try:
            trigger.onayla(k["task_id"], "oto-nobetci")
            print(f"  ONAYLANDI: {k['task_id']} (teslim: {k['ajan']})")
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
                    duzeltilen += 1
        except Exception:
            pass
    
    if duzeltilen == 0:
        print("  (düzeltilecek bir şey yok)")
    else:
        print(f"\n  Toplam: {duzeltilen} işlem")
    
    return 0