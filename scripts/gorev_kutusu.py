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

_KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_KOK))
sys.path.insert(0, str(_KOK / "src"))

# Windows konsolu (cp1254) Unicode ok/emoji karakterlerinde cokuyordu.
# Cikti akislarini UTF-8'e cevir; desteklenmeyen karakterlerde cokme yerine degistir.
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - eski Python / yonlendirilmis akis
        pass

from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402
from src.company_master.orchestrator import duzen  # noqa: E402
from src.company_master.orchestrator import isbirligi  # noqa: E402


def _ayristir_liste(deger: str | None) -> list[str]:
    if not deger:
        return []
    return [p.strip() for p in deger.split(",") if p.strip()]


def _hata(exc: Exception) -> int:
    print(f"HATA: {exc}", file=sys.stderr)
    return 1


def _talimat_bul(ajan: str, task_id: str, gorev: dict | None = None) -> str:
    """Görevin brifini döndür: önce tetik talimatı, yoksa pano `talimat` alanı."""
    for k in trigger.bekleyen_tetikler(ajan):
        if k.get("task_id") == task_id and (k.get("talimat") or "").strip():
            return str(k["talimat"]).strip()
    gorev = gorev if gorev is not None else (tb.gorev_getir(task_id) or {})
    return str(gorev.get("talimat") or "").strip()


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
        talimat = _talimat_bul(args.ajan, k["task_id"], gorev)
        if talimat:
            print(f"  TALIMAT: {talimat}")
        else:
            print("  ⚠️ TALIMAT YOK — brif yazilmadan alinamaz (orkestratore danis)")
        if gorev.get("dosyalar"):
            print(f"  KILITLI DOSYALAR: {', '.join(gorev['dosyalar'])}")
        print(f"  -> al: python scripts/gorev_kutusu.py al --ajan {args.ajan} --task-id {k['task_id']}")
    return 0


def cmd_al(args: argparse.Namespace) -> int:
    # Brif görünürlüğü: talimatsız görev alınamaz (--zorla ile bilinçli atlama).
    if not getattr(args, "zorla", False) and not _talimat_bul(args.ajan, args.task_id):
        print(
            f"HATA: {args.task_id} icin talimat (brif) yok. Once orkestrator "
            f"`gorev_at.py at --talimat ...` veya `gorev_guncelle(talimat=...)` ile brif yazmali; "
            f"bilincli atlamak icin --zorla kullan."
        )
        return 1
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


def cmd_basla(args: argparse.Namespace) -> int:
    """Tek kelime tetik: postayi oku, zinciri goster, otonom calisma yolunu bas.

    KAHIN yalnizca "basla" der; ajan bu ciktiyi okuyup 4 gorevi sirayla bitirir.
    """
    ajan = args.ajan
    bekleyen = trigger.bekleyen_tetikler(ajan)
    kalan = trigger.zincir_kalan(ajan)
    rol = trigger.AJAN_ROLU.get(ajan, "uretim")
    print(f"=== {trigger.ajan_goster(ajan)} OTONOM ZINCIR ===")
    if not bekleyen and not kalan:
        print("Posta bos, zincir yok. Orkestratore haber ver.")
        return 0
    sira = [k["task_id"] for k in bekleyen] + [k["task_id"] for k in kalan]
    print(f"Zincir ({len(sira)} gorev): {' -> '.join(sira)}\n")
    for tid in sira:
        g = tb.gorev_getir(tid) or {}
        print(f"  {tid} ({g.get('oncelik', '?')}) {g.get('baslik', '(pano basligi yok)')}")
        talimat = _talimat_bul(ajan, tid, g)
        print(f"    TALIMAT: {talimat or '⚠️ YOK — orkestratore danis'}")
        if g.get("dosyalar"):
            print(f"    KILITLI: {', '.join(g['dosyalar'])}")
    rapor = f"data/orchestrator/ZINCIR_rapor_{trigger._simdi()[:10]}_{rol}.md"
    print(f"""
KURAL (her gorev icin sirayla, DURMADAN):
  1) al     : python scripts/gorev_kutusu.py al --ajan {ajan} --task-id <ID>
  2) isi yap (AGENTS.md teslim kontrol listesi)
  3) denetim: python scripts/kodlama_denetim.py
  4) teslim : python scripts/gorev_kutusu.py teslim --ajan {ajan} --task-id <ID> --ozet "..."
     -> teslim sonrasi ZINCIR sonraki gorevi otomatik tetikler; postaya tekrar bak.
ZINCIR BITINCE (tum gorevler teslim):
  5) toplu raporu yaz: {rapor}
  6) postala: python scripts/gorev_kutusu.py rapor-postala --ajan {ajan} \\
       --rapor "{rapor}" --baslik "zincir bitti: {len(sira)} gorev"
Arada KAHIN'e soru sorma; blokaj varsa raporda yaz.""")
    return 0


def cmd_rapor_postala(args: argparse.Namespace) -> int:
    """Zincir bitis raporunu orkestratorun postasina dusur."""
    yol = Path(args.rapor)
    if not yol.is_absolute():
        yol = Path(__file__).resolve().parents[1] / args.rapor
    if not yol.exists():
        return _hata(FileNotFoundError(f"Rapor dosyasi yok: {args.rapor}"))
    kayit = trigger.rapor_postala(args.ajan, args.baslik, args.rapor, args.hedef)
    print(f"RAPOR POSTALANDI: {args.ajan} -> {kayit['ajan']} ({args.rapor})")
    return 0


def cmd_raporlar(args: argparse.Namespace) -> int:
    """Orkestratorun postasina dusen zincir raporlarini listele."""
    kayitlar = trigger.raporlar(args.ajan)
    if not kayitlar:
        print("Rapor postasi bos.")
        return 0
    print(f"{len(kayitlar)} zincir raporu:")
    for k in kayitlar:
        print(f"\n  {trigger.ajan_goster(k.get('gonderen'))}  ({k['tarih']})")
        print(f"  {k.get('talimat', '')}")
        print(f"  -> {k.get('rapor_yolu', '')}")
    return 0


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
    """Tum teslim edilen gorevleri onayla ve zinciri devam ettir.

    S-07 (sahip karari 2026-09-16): P0/P1 gorevler atlanir, roo elle onaylar.
    """
    duzeltilen = 0
    kuyruk = trigger.onay_bekleyenler()
    for k in kuyruk:
        try:
            uygun, gerekce = trigger.otomatik_onaylanabilir(k["task_id"])
            if not uygun:
                print(f"  ELLE ONAY GEREKLI: {k['task_id']} -> roo ({gerekce})")
                continue
            trigger.onayla(k["task_id"], "oto-nobetci")
            print(f"  ONAYLANDI: {k['task_id']} (teslim: {k['ajan']})")
            duzeltilen += 1
        except Exception as e:
            print(f"  HATA: {k['task_id']} - {e}")

    for ajan in trigger.AJANLAR:
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


def cmd_bakim(args: argparse.Namespace) -> int:
    """Pano hijyeni: cift kayit, takili tetik, bayat zincir, blokaj otomasyonu."""
    if args.rapor:
        t = duzen.pano_tarama()
        print("[TARAMA] (dokunulmadi)")
        print(f"  cift kayit: {t['cift_kayit'] or 'yok'}")
        for s in t["takili_tetik"]:
            print(f"  takili: {s}")
        if not t["takili_tetik"]:
            print("  takili tetik: yok")
        print(f"  blocked: {', '.join(t['blocked']) or 'yok'}")
        return 0
    r = duzen.pano_bakim()
    print("[BAKIM] uygulandi:")
    print(f"  dedupe: {r['dedupe']} | tetik esit: {r['tetik_esit']}")
    for z in r["zincir"]:
        print(f"  zincir: {z}")
    print(f"  blokaj acilan: {', '.join(r['acilan']) or 'yok'}")
    print(f"  blokaj kapanan: {', '.join(r['kapanan']) or 'yok'}")
    return 0


def cmd_ozet(args: argparse.Namespace) -> int:
    """Token dostu tek satirlik pano ozeti."""
    print(duzen.ozet_rapor())
    return 0


def _ceyrek(kayit: dict, bugun: str) -> str:
    """Kaydin tamamlanma tarihinden ceyregi hesapla; tarih yoksa bugununki.

    `bitis` alani ISO ("2026-09-21T...") ya da bozuk/bos olabilir (panoda
    "None", 4 karakterlik artiklar gozlemlendi) — ayristirilamayan her deger
    bugunun ceyregine duser.
    """
    ham = str(kayit.get("bitis") or "")[:10]
    if len(ham) < 7 or not ham[:4].isdigit() or not ham[5:7].isdigit():
        ham = bugun[:10]
    return f"{ham[:4]}-Q{(int(ham[5:7]) - 1) // 3 + 1}"


def arsiv_bol(pano: list[dict], bugun: str) -> tuple[list[dict], dict[str, list[dict]]]:
    """Panoyu (aktif kalanlar, {ceyrek: tasinacak kayitlar}) olarak ayir.

    Terminal durum listesi `tb.KAPALI_DURUMLAR` — tek kaynak, kopyalanmaz.
    """
    aktif: list[dict] = []
    kovalar: dict[str, list[dict]] = {}
    for g in pano:
        if g.get("durum") in tb.KAPALI_DURUMLAR:
            kovalar.setdefault(_ceyrek(g, bugun), []).append(g)
        else:
            aktif.append(g)
    return aktif, kovalar


def cmd_arsivle(args: argparse.Namespace) -> int:
    """Terminal kayitlari ceyreklik arsiv dosyalarina tasi (idempotent).

    Her ceyrek tekrar calistirilabilir: arsiv dosyasi varsa uzerine yazilmaz,
    ayni task_id ikinci kez eklenmez.
    """
    pano = tb._read_json(tb.TASK_BOARD)
    bugun = trigger._simdi()
    aktif, kovalar = arsiv_bol(pano, bugun)
    tasinan = sum(len(v) for v in kovalar.values())
    print(f"{tasinan} kayit tasinacak, aktif panoda {len(aktif)} kalacak.")
    for ceyrek in sorted(kovalar):
        print(f"  {ceyrek}: {len(kovalar[ceyrek])} kayit")
    if args.kuru:
        print("(--kuru: hicbir dosya yazilmadi)")
        return 0
    for ceyrek, kayitlar in sorted(kovalar.items()):
        yol = tb.STATE_DIR / f"task_board_arsiv_{ceyrek}.json"
        mevcut = tb._read_json(yol) if yol.exists() else []
        bilinen = {str(k.get("task_id")) for k in mevcut}
        yeni = [k for k in kayitlar if str(k.get("task_id")) not in bilinen]
        tb._write_json(yol, mevcut + yeni)
        print(f"  YAZILDI {yol.name}: +{len(yeni)} (toplam {len(mevcut) + len(yeni)})")
    tb._write_json(tb.TASK_BOARD, aktif)
    print(f"AKTIF PANO: {len(aktif)} kayit")
    return 0


def cmd_yardim(args: argparse.Namespace) -> int:
    """ORCH-12: Bosta ajanlar + onerileri goster."""
    bos = isbirligi.bos_ajanlar()
    if not bos:
        print("Bos ajan yok (tum ajanlar meguldu).")
        return 0
    print(f"Bos ajanlar ({len(bos)}): {', '.join(bos)}")
    for ajan in bos:
        adaylar = isbirligi.yardim_edilebilir(ajan, limit=3)
        if adaylar:
            print(f"\n  [{ajan}] oneriler:")
            for a in adaylar:
                print(f"    {a['task_id']} ({a['rol']}) — {a['baslik']}")
        else:
            print(f"\n  [{ajan}] oneri yok.")
    return 0


def cmd_destek_al(args: argparse.Namespace) -> int:
    """ORCH-12: Destek gorevi al (tests/docs/plans altina yazar)."""
    try:
        sonuc = isbirligi.destek_al(args.ajan, args.hedef, args.rol)
    except (ValueError, Exception) as exc:
        return _hata(exc)
    print(f"DESTEK ALINDI: {sonuc['gorev']['task_id']} -> {args.ajan}")
    print(f"  Hedef: {args.hedef} | Rol: {args.rol}")
    print(f"  -> tetik dosyasina yazildi")
    return 0


def cmd_devret(args: argparse.Namespace) -> int:
    """Gorevi baska ajana devret: sahip + kilitler + yeni ajana tetik."""
    g = tb.gorev_getir(args.task_id)
    if not g:
        return _hata(ValueError(f"Gorev yok: {args.task_id}"))
    eski = g["sahip"]
    # Eski ajanin bekleyen/alindi tetigi -> kaldir
    try:
        kayitlar = trigger._tetikleri_oku(eski)
        kalan = [k for k in kayitlar if not (k["task_id"] == args.task_id and k["durum"] in ("bekliyor", "alindi"))]
        if len(kalan) != len(kayitlar):
            trigger._tetikleri_yaz(kalan, eski)
    except Exception:
        pass
    # Kilit sahipligini transfer et
    try:
        kilitler = tb._read_json(tb.FILE_LOCKS)
        for d, l in kilitler.items():
            if l.get("task_id") == args.task_id:
                l["sahip"] = args.yeni_ajan
        tb._write_json(tb.FILE_LOCKS, kilitler)
    except Exception:
        pass
    tb.gorev_guncelle(args.task_id, sahip=args.yeni_ajan,
                      **{"not": f"Devredildi: {eski} -> {args.yeni_ajan} ({args.neden or '-'})"})
    trigger.tetik_ekle(args.task_id, args.yeni_ajan,
                       f"DEVROLDU ({eski} icin). " + (args.neden or ""))
    print(f"DEVRETILDI: {args.task_id} {eski} -> {args.yeni_ajan} + tetik dustu")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ORCH-08 — Ajan posta kutusu + kontrolör onay")

    sub = parser.add_subparsers(dest="komut", required=True)

    bak_p = sub.add_parser("bak", help="Ajanın posta kutusunu göster")
    bak_p.add_argument("--ajan", required=True, help="Ajan adı (kilo, roo, vs.)")
    bak_p.set_defaults(func=cmd_bak)

    basla_p = sub.add_parser("basla", help="Tek kelime tetik: posta+zincir+otonom talimat")
    basla_p.add_argument("--ajan", required=True)
    basla_p.set_defaults(func=cmd_basla)

    rapor_p = sub.add_parser("rapor-postala", help="Zincir bitis raporunu orkestratore postala")
    rapor_p.add_argument("--ajan", required=True, help="Raporu yazan ajan")
    rapor_p.add_argument("--rapor", required=True, help="Rapor dosya yolu")
    rapor_p.add_argument("--baslik", required=True, help="Tek satir ozet")
    rapor_p.add_argument("--hedef", default="ihsan", help="Postalanacak ajan (varsayilan ihsan)")
    rapor_p.set_defaults(func=cmd_rapor_postala)

    raporlar_p = sub.add_parser("raporlar", help="Postaya dusen zincir raporlarini listele")
    raporlar_p.add_argument("--ajan", default="ihsan")
    raporlar_p.set_defaults(func=cmd_raporlar)

    al_p = sub.add_parser("al", help="Tetiği al (görevi aktif yap)")
    al_p.add_argument("--ajan", required=True)
    al_p.add_argument("--task-id", required=True)
    al_p.add_argument("--zorla", action="store_true", help="Talimatsız görevi yine de al")
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

    bakim_p = sub.add_parser("bakim", help="Pano hijyeni: cift kayit, takili tetik, blokaj")
    bakim_p.add_argument("--rapor", action="store_true", help="Sadece rapor, duzeltme yok")
    bakim_p.set_defaults(func=cmd_bakim)

    ozet_p = sub.add_parser("ozet", help="Token dostu tek satirlik pano ozeti")
    ozet_p.set_defaults(func=cmd_ozet)

    arsivle_p = sub.add_parser("arsivle", help="Terminal kayitlari ceyreklik arsive tasi")
    arsivle_p.add_argument("--kuru", action="store_true", help="Yazma yok, sadece sayi raporu")
    arsivle_p.set_defaults(func=cmd_arsivle)

    yardim_p = sub.add_parser("yardim", help="ORCH-12: Bosta ajanlar + onerileri goster")
    yardim_p.set_defaults(func=cmd_yardim)

    destek_al_p = sub.add_parser("destek-al", help="ORCH-12: Destek gorevi al")
    destek_al_p.add_argument("--ajan", required=True)
    destek_al_p.add_argument("--hedef", required=True)
    destek_al_p.add_argument("--rol", choices=["test", "arastirma"], default="test")
    destek_al_p.set_defaults(func=cmd_destek_al)

    devret_p = sub.add_parser("devret", help="Gorevi baska ajana devret (sahip+kilit+tetik)")
    devret_p.add_argument("--task-id", required=True)
    devret_p.add_argument("--yeni-ajan", required=True)
    devret_p.add_argument("--neden", default="")
    devret_p.set_defaults(func=cmd_devret)

    args = parser.parse_args()
    # D-33 ajan adı kuralı: "Ajan kilo" / "Kilo" / "kilo_code" → "kilo".
    # Tüm alt komutlar tek noktadan kanonik ada çevrilir.
    for alan in ("ajan", "yeni_ajan", "hedef"):
        deger = getattr(args, alan, None)
        if deger:
            try:
                setattr(args, alan, trigger.ajan_normalize(deger))
            except trigger.TriggerError as exc:
                return _hata(exc)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
