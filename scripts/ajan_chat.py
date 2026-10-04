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
  yorum         — Mesaja yanıt ekle (kime, cevap_index, mesaj) (Mesaj 6 · D-3xx)
  liderlik      — Ajan liderlik tablosu: görev+bulgu+mesaj sayısı (Mesaj 6 · Yol A)

Örnek:
  python scripts/ajan_chat.py ac ihsan UI-01 "Button hover eksik"
  python scripts/ajan_chat.py ozet --durum acik
  python scripts/ajan_chat.py bulgula "Tasarım (D-192)" "Font boyut tutarsız" --link "data/..."
  python scripts/ajan_chat.py yorum utku 42 "Kabul, SLA'yi 15dk yaptim" --kimden ihsan
  python scripts/ajan_chat.py liderlik
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
if str(_KOK / "scripts") not in sys.path:
    sys.path.insert(0, str(_KOK / "scripts"))

from company_master import chat
from company_master.orchestrator import task_board as tb  # noqa: E402
from company_master.orchestrator import trigger  # noqa: E402
import bulgu_defteri  # noqa: E402  (scripts/ — liderlik bulgu sayimi icin)
import chat_al  # noqa: E402  (scripts/ — liderlik mesaj sayimi icin)
import chat_gonder  # noqa: E402  (scripts/ — yorum yazimi icin, tek-yazici D-211)


def cmd_ac(args: argparse.Namespace) -> int:
    """Sorun aç."""
    try:
        # D-336: --kimden bosken sabit "orkestrator" YAZILMAZ (ORCH-KIMLIK-ZINCIRI-01
        # deseni, D-306 ile ayni kalip — yorum komutuyla tutarli).
        kimden_ham = (args.kimden or "").strip() or (chat_gonder.ajan_kimligi() or "")
        if not kimden_ham:
            print(
                "❌ Hata: gonderen ajan belirsiz. --kimden <ajan> verin veya "
                "HUGINN_AJAN ortam degiskenini tanimlayin.",
                file=sys.stderr,
            )
            return 1
        # D-287: ac yanlis kapi olabilir. Baskasinin acik kaydi varsa uyar
        # ama ENGELLEME (PO karari: uyari yeter).
        sahipler = chat.acik_sahipler(args.task_id, kimden_ham)
        if sahipler:
            print(
                f"⚠️  {args.task_id} altinda acik kayit var: {', '.join(sahipler)}. "
                f"Cevap yaziyorsan 'kapat --karar' veya 'guncelle' kullan (D-286).",
                file=sys.stderr,
            )
        satir = chat.ac(
            ajan=args.ajan,
            task_id=args.task_id,
            sorun=args.sorun,
            cozum=args.cozum or "",
            kimden=kimden_ham,
            onem=args.onem or "orta",
        )
        print(f"✅ Sorun kaydedildi: {satir['kimden']} → {satir['ajan']} | {satir['task_id']} ({satir['timestamp']}) [önem={satir['onem']}]")
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


def cmd_yorum(args: argparse.Namespace) -> int:
    """Mesaja yanıt ekle (Mesaj 6 · en fazla 2 yorum / kişi / hedef mesaj)."""
    try:
        kimden_ham = (args.kimden or "").strip()
        if not kimden_ham:
            kimden_ham = chat_gonder.ajan_kimligi()
        kimden_norm = trigger.ajan_normalize(kimden_ham)
        mevcut = [
            k for k in chat_al._satirlari_yukle()
            if k.get("type") == "yorum"
            and k.get("cevap_index") == args.cevap_index
            and k.get("kimden") == kimden_norm
        ]
        if len(mevcut) >= 2:
            print(
                f"❌ Hata: {kimden_norm} bu mesaja zaten 2 yorum yazdı (satır {args.cevap_index}).",
                file=sys.stderr,
            )
            return 1
        kayit = chat_gonder.gonder(
            kime=args.kime,
            tip="yorum",
            mesaj=args.mesaj,
            task_id=args.task_id or "",
            kimden=args.kimden or None,
            cevap_index=args.cevap_index,
        )
        print(
            f"✅ Yorum gönderildi: {kayit['kimden']} → {kayit['kime']} "
            f"(satır {args.cevap_index}) {kayit['tarih']}"
        )
        return 0
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        return 1


def liderlik_verisi() -> list[dict]:
    """Gorev/bulgu/mesaj sayimini hesaplar, azalan siralar (Mesaj 6 · Yol A).

    CLI (`cmd_liderlik`) ve Streamlit admin paneli ortak kullanir — tek hesap, iki gorunum.
    """
    ajanlar = [a for a in trigger.AJANLAR if a != "mimir"]

    gorev_sayim: dict[str, int] = {a: 0 for a in ajanlar}
    for g in tb.gorev_listesi("done"):
        sahip = g.get("sahip")
        if sahip in gorev_sayim:
            gorev_sayim[sahip] += 1

    bulgu_sayim: dict[str, int] = {a: 0 for a in ajanlar}
    for satir in bulgu_defteri._veri_satirlari(bulgu_defteri._coz(None)):
        alanlar = [p.strip() for p in satir.split("|")]
        if len(alanlar) >= 3 and alanlar[2] in bulgu_sayim:
            bulgu_sayim[alanlar[2]] += 1

    mesaj_sayim: dict[str, int] = {a: 0 for a in ajanlar}
    for m in chat_al._satirlari_yukle():
        kimden = m.get("kimden")
        if kimden in mesaj_sayim:
            mesaj_sayim[kimden] += 1

    siralama = sorted(
        ajanlar,
        key=lambda a: (gorev_sayim[a], bulgu_sayim[a], mesaj_sayim[a]),
        reverse=True,
    )
    return [
        {"ajan": a, "gorev": gorev_sayim[a], "bulgu": bulgu_sayim[a], "mesaj": mesaj_sayim[a]}
        for a in siralama
    ]


def cmd_liderlik(args: argparse.Namespace) -> int:
    """Ajan liderlik tablosu: done görev + bulgu satırı + mesaj sayısı (Mesaj 6 · Yol A)."""
    try:
        satirlar = liderlik_verisi()
        print("🏆 Liderlik Tablosu (Mesaj 6 · Yol A)")
        print(f"{'#':<3}{'Ajan':<10}{'Gorev(done)':>14}{'Bulgu':>8}{'Mesaj':>8}")
        for i, s in enumerate(satirlar, 1):
            print(f"{i:<3}{s['ajan']:<10}{s['gorev']:>14}{s['bulgu']:>8}{s['mesaj']:>8}")
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
    p_ac.add_argument("--kimden", "-k", default="", help="Gönderen ajan adı (boşsa kimlik zinciri çözer, D-336)")
    p_ac.add_argument(
        "--onem", "-o",
        choices=["kritik", "yuksek", "orta", "dusuk"],
        default="orta",
        help="Önem derecesi (varsayılan: orta)"
    )
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

    # yorum: Mesaja yanıt (Mesaj 6)
    p_yorum = subparsers.add_parser("yorum", help="Mesaja yanıt ekle (max 2/kişi/hedef)")
    p_yorum.add_argument("kime", help="Alıcı ajan (veya hepsi)")
    p_yorum.add_argument("cevap_index", type=int, help="Hedef mesajın satır no'su (chat_al _satir)")
    p_yorum.add_argument("mesaj", help="Yorum metni")
    p_yorum.add_argument("--task-id", "-i", default="", help="İlgili görev kimliği (opsiyonel)")
    p_yorum.add_argument("--kimden", "-k", default="", help="Gönderen ajan (boşsa kimlik zinciri çözer)")
    p_yorum.set_defaults(func=cmd_yorum)

    # liderlik: Ajan liderlik tablosu (Mesaj 6 · Yol A)
    p_liderlik = subparsers.add_parser("liderlik", help="Ajan liderlik tablosu")
    p_liderlik.set_defaults(func=cmd_liderlik)

    args = ap.parse_args(argv)

    if not args.komut:
        ap.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
