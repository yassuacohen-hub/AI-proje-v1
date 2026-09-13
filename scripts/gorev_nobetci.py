# -*- coding: utf-8 -*-
"""ORCH-09: Otomatik tetikleme nobetcisi.

AJAN tarafı (oturum başında poll):
    python scripts/gorev_nobetci.py nobet          # tek gezinti
    python scripts/gorev_nobetci.py tetik-ayarla --ajan kilo --task-id X --sure-sn 120
KONTROLÖR tarafı:
    python scripts/gorev_nobetci.py kur --dakika 1  # zamanlayıcı kur (deneme)
    python scripts/gorev_nobetci.py durum
    python scripts/gorev_nobetci.py kaldir          # zamanlayıcı + ayarları kaldır
    python scripts/gorev_nobetci.py uyari-goster --ajan kilo --task-id X

Geri almak için: ``python scripts/gorev_nobetci.py kaldir`` (tek komut).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import nobetci
from src.company_master.orchestrator import trigger

NOBETCI_GOREV = "HuginnData-Nobetci"
BAT_YOL = str(Path(__file__).resolve().parent / "gorev_nobetci.bat")


def _hata(exc: Exception) -> int:
    print(f"HATA: {exc}", file=sys.stderr)
    return 1


def _gorev_ac(ajan: str, task_id: str, baslik: str = "") -> None:
    if not tb.gorev_getir(task_id):
        tb.gorev_ekle(task_id, baslik or f"{task_id} tetik testi", ajan, "P1")
    trigger.tetik_ekle(task_id, ajan, talimat="tetik testi")


# ---- nobet ----

def cmd_nobet(args: argparse.Namespace) -> int:
    ayar = nobetci.nobetci_ayar_oku()
    gecenler = nobetci.nobet_tut(ayar=ayar)
    if gecenler:
        print(f"Nobet: {len(gecenler)} tetik firlatildi:")
        for g in gecenler:
            print(f"  -> {g['task_id']} ({g['ajan']}): {g['tetik_sayisi']}x — {g['alarm_dosyasi']}")
    else:
        print(f"Nobet: geciken tetik yok (kademe {ayar.get('kademe_sn')} sn).")
    return 0


# ---- kur / kaldir ----

def _bat_olustur() -> None:
    root = str(Path(tb.ROOT))
    yol = Path(__file__).resolve().parent / "gorev_nobetci.bat"
    icerik = (
        "@echo off\r\n"
        f'cd /d "{root}"\r\n'
        f'python scripts\\gorev_nobetci.py nobet >> data\\orchestrator\\nobetci.log 2>&1\r\n'
    )
    yol.write_text(icerik, encoding="utf-8")


def cmd_kur(args: argparse.Namespace) -> int:
    ayar = {"kademe_sn": args.dakika * 60, "kanallar": ["log", "alarm_dosyasi", "ses"], "telegram": args.telegram}
    nobetci.nobetci_ayar_yaz(ayar)
    _bat_olustur()
    tr = f'cmd /c "{BAT_YOL}"'
    subprocess.run(["schtasks", "/Create", "/TN", NOBETCI_GOREV, "/TR", tr,
                    "/SC", "MINUTE", "/MO", str(args.dakika), "/F"], check=True)
    print(f"Nobetci kuruldu: her {args.dakika} dakika bir calisir (kademe {ayar['kademe_sn']} sn).")
    return 0


def cmd_kaldir(args: argparse.Namespace) -> int:
    try:
        subprocess.run(["schtasks", "/Delete", "/TN", NOBETCI_GOREV, "/F"],
                       check=False, capture_output=True)
    except Exception as exc:
        print(f"[uwarning] zamanlayici silinemedi: {exc}")
    nobetci.nobetci_ayar_yaz({"devre_disi": True})
    print("Nobetci kaldirildi (zamanlayici silindi, ayarlar devre disi).")
    return 0


# ---- durum ----

def cmd_durum(args: argparse.Namespace) -> int:
    try:
        r = subprocess.run(["schtasks", "/Query", "/TN", NOBETCI_GOREV, "/fo", "LIST", "/v"],
                           capture_output=True, text=True, check=False)
        print(r.stdout.strip() if r.returncode == 0 else "Zamanlayıcı kaydı yok (`kur` ile başlatın).")
    except Exception as exc:
        print(f"Zamanlayıcı sorgulama hatasi: {exc}")
    ayar = nobetci.nobetci_ayar_oku()
    print(f"\nAyarlar: kademe={ayar.get('kademe_sn')} sn, kanallar={ayar.get('kanallar')}, devre_disi={ayar.get('devre_disi')}")
    gecenler = nobetci.geciken_tetikler()
    print(f"Geciken tetik sayisi: {len(gecenler)}")
    for g in gecenler:
        print(f"  -> {g['task_id']} ({g['ajan']}): {g['gecikme_dk']} dk gecikmis")
    return 0

# ---- tetik-ayarla (canlı test) ----

def cmd_tetik_ayarla(args: argparse.Namespace) -> int:
    _gorev_ac(args.ajan, args.task_id, args.baslik)
    nobetci.tetik_gecikmis_yap(args.ajan, args.task_id, args.sure_sn)
    tetik = trigger.bekleyen_tetikler(args.ajan)
    t = next((k for k in tetik if k["task_id"] == args.task_id), {})
    print(f"Tetik hazirlaniyor: {args.task_id} ({args.ajan}) "
          f"{args.sure_sn} sn gerice — {t.get('tarih')}")
    return 0


# ---- uyari-goster ----

def cmd_uyari_goster(args: argparse.Namespace) -> int:
    alarm_yol = tb.STATE_DIR / "triggers" / f"{args.ajan}.ALARM.json"
    if not alarm_yol.exists():
        print(f"Alarm dosyasi yok: {alarm_yol}")
        return 0
    alarm = json.loads(alarm_yol.read_text(encoding="utf-8-sig"))
    alarm = alarm if isinstance(alarm, list) else [alarm]
    girdi = next((a for a in alarm if a.get("task_id") == args.task_id), None)
    if not girdi:
        print(f"Alarm bulunamadi: {args.task_id}")
        return 0
    print(json.dumps(girdi, ensure_ascii=False, indent=2))
    nobetci._ses_uyarisi()
    print("(ses caldi)")
    return 0


# ---- main ----

def main() -> int:
    parser = argparse.ArgumentParser(description="ORCH-09: Otomatik tetikleme nobetcisi")
    alt = parser.add_subparsers(dest="komut", required=True)

    p = alt.add_parser("nobet", help="Tek nobet gezintisi"); p.set_defaults(func=cmd_nobet)
    p = alt.add_parser("kur", help="Zamanlayici kur (deneme)")
    p.add_argument("--dakika", type=int, default=1, help="Periyot dakikasi")
    p.add_argument("--telegram", action="store_true", help="Telegram bildirimi")
    p.set_defaults(func=cmd_kur)
    p = alt.add_parser("kaldir", help="Zamanlayici + ayarları kaldır"); p.set_defaults(func=cmd_kaldir)
    p = alt.add_parser("durum", help="Zamanlayıcı + ayar + geciken tetikler"); p.set_defaults(func=cmd_durum)
    p = alt.add_parser("tetik-ayarla", help="Test: gecikmis tetik olustur")
    p.add_argument("--ajan", required=True); p.add_argument("--task-id", required=True)
    p.add_argument("--sure-sn", type=int, default=120); p.add_argument("--baslik", default="")
    p.set_defaults(func=cmd_tetik_ayarla)
    p = alt.add_parser("uyari-goster", help="ALARM dosyasini goruntule + ses dene")
    p.add_argument("--ajan", required=True); p.add_argument("--task-id", required=True)
    p.set_defaults(func=cmd_uyari_goster)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
