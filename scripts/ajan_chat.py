#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""D-192: Ajan Chat Sistemi — CLI.

Komutlar:
  ac            — Sorun aç (ajan, task_id, sorun)
  guncelle      — Çözümü güncelle (task_id, sorun_index, cozum, durum)
  kapat         — Sorunukapalı işaretle (task_id, sorun_index, karar)
  oku           — Sorunları oku (--task_id, --son)
  ozet          — Sorunların özetini göster (--durum)
  bulgula       — Tasarım eleştirisi kaydı (konu, bulgu, --link)

Örnek:
  python scripts/ajan_chat.py ac ihsan UI-01 "Button hover eksik"
  python scripts/ajan_chat.py ozet --durum acik
  python scripts/ajan_chat.py bulgula "Tasarım (D-192)" "Font boyut tutarsız" --link "data/..."
"""

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_KOK = Path(__file__).resolve().parent.parent
if str(_KOK / "src") not in sys.path:
    sys.path.insert(0, str(_KOK / "src"))

from company_master import chat


def cmd_ac(args: argparse.Namespace) -> int:
    """Sorun aç."""
    try:
        satir = chat.ac(
            ajan=args.ajan,
            task_id=args.task_id,
            sorun=args.sorun,
            cozum=args.cozum or "",
            kimden=args.kimden or "orkestrator",
        )
        print(f"✅ Sorun kaydedildi: {satir['kimden']} → {satir['ajan']} | {satir['task_id']} ({satir['timestamp']})")
        return 0
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        return 1


def cmd_guncelle(args: argparse.Namespace) -> int:
    """Çözümü güncelle."""
    try:
        satir = chat.guncelle(
            task_id=args.task_id,
            sorun_index=args.sorun_index,
            cozum_guncel=args.cozum or "",
            durum=args.durum,
        )
        if satir:
            print(f"✅ Güncellenmiş: {satir['task_id']} → {satir['durum']}")
            return 0
        else:
            print(f"❌ Sorun bulunamadı: {args.task_id}[{args.sorun_index}]", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        return 1


def cmd_kapat(args: argparse.Namespace) -> int:
    """Sorunukapalı işaretle."""
    try:
        satir = chat.kapat(
            task_id=args.task_id,
            sorun_index=args.sorun_index,
            karar=args.karar or "",
        )
        if satir:
            print(f"✅ Kapatıldı: {satir['task_id']} (durum={satir['durum']})")
            return 0
        else:
            print(f"❌ Sorun bulunamadı: {args.task_id}[{args.sorun_index}]", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        return 1


def cmd_oku(args: argparse.Namespace) -> int:
    """Sorunları oku."""
    try:
        satirlar = chat.oku(task_id=args.task_id, son=args.son)
        
        if not satirlar:
            print("Sorun kaydı yok.")
            return 0
        
        for i, s in enumerate(satirlar, 1):
            print(
                f"\n{i}. [{s['ajan'].upper()}] {s['task_id']} ({s['durum']})\n"
                f"   Sorun: {s['sorun']}\n"
                f"   Çözüm: {s['cozum']}\n"
                f"   Zaman: {s['timestamp']}"
            )
        
        print(f"\nToplam: {len(satirlar)} sorun")
        return 0
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        return 1


def cmd_ozet(args: argparse.Namespace) -> int:
    """Sorunların özetini göster."""
    try:
        acik = chat.ozet("acik")
        cokundurmus = chat.ozet("cokundurmus")
        cozuldu = chat.ozet("cozuldu")
        
        print(
            f"📊 Ajan Chat Özeti:\n"
            f"  🔴 Açık Sorunlar:      {len(acik)}\n"
            f"  🟡 Çözüm Bekleniyor:   {len(cokundurmus)}\n"
            f"  🟢 Çözüldü:            {len(cozuldu)}\n"
            f"  —————————————————————\n"
            f"  Toplam:                {len(acik) + len(cokundurmus) + len(cozuldu)}"
        )
        
        # Filtre varsa göster
        if args.durum:
            satirlar = chat.ozet(args.durum)
            print(f"\n{args.durum.upper()} sorunlar ({len(satirlar)}):")
            for i, s in enumerate(satirlar[:5], 1):
                print(f"  {i}. [{s['ajan'].upper()}] {s['task_id']}: {s['sorun'][:50]}")
            if len(satirlar) > 5:
                print(f"  ... ve {len(satirlar) - 5} daha")
        
        return 0
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        return 1


def cmd_bulgula(args: argparse.Namespace) -> int:
    """Tasarım eleştirisi kaydı."""
    try:
        satir = chat.bulgula(
            konu=args.konu,
            bulgu=args.bulgu,
            link=args.link or "",
        )
        print(f"✅ Eleştiri kaydedildi: {satir['konu']} ({satir['timestamp']})")
        return 0
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    """Ana CLI entry point."""
    ap = argparse.ArgumentParser(
        prog="ajan_chat",
        description="D-192: Ajan Chat Sistemi — Sorun ve çözüm takibi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    subparsers = ap.add_subparsers(dest="komut", help="Komut seçin")
    
    # ac: Sorun aç
    p_ac = subparsers.add_parser("ac", help="Sorun aç")
    p_ac.add_argument("ajan", help="Kime — hedef ajan adı (ihsan/utku/salih/yasu)")
    p_ac.add_argument("task_id", help="Görev ID (örn. UI-01)")
    p_ac.add_argument("sorun", help="Sorun açıklaması (1-200 karakter)")
    p_ac.add_argument("--cozum", "-c", help="İlk çözüm önerisi (isteğe bağlı)")
    p_ac.add_argument("--kimden", "-k", default="orkestrator", help="Gönderen ajan adı (varsayılan: orkestrator)")
    p_ac.set_defaults(func=cmd_ac)
    
    # guncelle: Çözümü güncelle
    p_guncelle = subparsers.add_parser("guncelle", help="Çözümü güncelle")
    p_guncelle.add_argument("task_id", help="Görev ID")
    p_guncelle.add_argument("sorun_index", type=int, help="Sorun index (0-based)")
    p_guncelle.add_argument("--cozum", "-c", help="Güncellenmiş çözüm metni")
    p_guncelle.add_argument(
        "--durum", "-d",
        choices=["cokundurmus", "cozuldu"],
        default="cokundurmus",
        help="Yeni durum (varsayılan: cokundurmus)"
    )
    p_guncelle.set_defaults(func=cmd_guncelle)
    
    # kapat: Sorunukapalı işaretle
    p_kapat = subparsers.add_parser("kapat", help="Sorunukapalı işaretle")
    p_kapat.add_argument("task_id", help="Görev ID")
    p_kapat.add_argument("sorun_index", type=int, help="Sorun index")
    p_kapat.add_argument("--karar", "-k", help="Karar notu (isteğe bağlı)")
    p_kapat.set_defaults(func=cmd_kapat)
    
    # oku: Sorunları oku
    p_oku = subparsers.add_parser("oku", help="Sorunları oku")
    p_oku.add_argument("--task_id", "-t", help="Belirli göreve filtrele")
    p_oku.add_argument("--son", "-s", type=int, help="Son N satırı al")
    p_oku.set_defaults(func=cmd_oku)
    
    # ozet: Özetini göster
    p_ozet = subparsers.add_parser("ozet", help="Sorunların özetini göster")
    p_ozet.add_argument(
        "--durum", "-d",
        choices=["acik", "cokundurmus", "cozuldu"],
        help="Belirli durum ile filtrele"
    )
    p_ozet.set_defaults(func=cmd_ozet)
    
    # bulgula: Tasarım eleştirisi
    p_bulgula = subparsers.add_parser("bulgula", help="Tasarım eleştirisi kaydı")
    p_bulgula.add_argument("konu", help="Başlık (örn. 'Tasarım Belgesi (D-192)')")
    p_bulgula.add_argument("bulgu", help="Eleştiri/görüş metni")
    p_bulgula.add_argument("--link", "-l", help="İlgili dosya/karar linki")
    p_bulgula.set_defaults(func=cmd_bulgula)
    
    args = ap.parse_args(argv)
    
    if not args.komut:
        ap.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
