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
import re
import subprocess
import sys
from datetime import date
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

import importlib.util as _ilu  # noqa: E402

_spec = _ilu.spec_from_file_location(
    "bulgu_defteri", Path(__file__).resolve().parent / "bulgu_defteri.py"
)
bulgu = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(bulgu)

from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402
from src.company_master.orchestrator import duzen  # noqa: E402
from src.company_master.orchestrator import isbirligi  # noqa: E402
from src.company_master import chat  # noqa: E402


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


def _yedek_blogu() -> None:
    """B-06: denetimde elenen yedek gorevler ayri blokta gorunur."""
    yedekler = [t for t in tb.gorev_listesi() if t.get("durum") == "yedek"]
    if not yedekler:
        return
    print(f"\n--- YEDEK GOREVLER ({len(yedekler)}) — siradaki tur adaylari, atanmaz ---")
    for t in yedekler:
        print(f"  {t['task_id']}  ({t.get('oncelik', '?')})  {t.get('baslik', '')}")


def cmd_bak(args: argparse.Namespace) -> int:
    bekleyen = trigger.bekleyen_tetikler(args.ajan)
    if not bekleyen:
        print(f"[{args.ajan}] posta kutusu bos.")
        _yedek_blogu()
        return 0
    print(f"[{args.ajan}] {len(bekleyen)} bekleyen gorev:")
    for k in bekleyen:
        gorev = tb.gorev_getir(k["task_id"]) or {}
        print(f"\n  {k['task_id']}  ({gorev.get('oncelik', '?')})  tetik: {k['tarih']}")
        print(f"  {gorev.get('baslik', '(pano basligi yok)')}")
        if k.get("uyari_tarihi"):
            # D-236: uyarı bilgisi tetik kaydının kendisinde; ALARM kopyası kaldırıldı.
            print(f"  ⚠️ UYARI ({k.get('uyari_sayisi', '?')}x) — tetik {k['uyari_tarihi']}'da firlatilmisti")
        talimat = _talimat_bul(args.ajan, k["task_id"], gorev)
        if talimat:
            print(f"  TALIMAT: {talimat}")
        else:
            print("  ⚠️ TALIMAT YOK — brif yazilmadan alinamaz (orkestratore danis)")
        if gorev.get("dosyalar"):
            print(f"  KILITLI DOSYALAR: {', '.join(gorev['dosyalar'])}")
        print(f"  -> al: python scripts/gorev_kutusu.py al --ajan {args.ajan} --task-id {k['task_id']}")
    _yedek_blogu()
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
    gorev = tb.gorev_getir(args.task_id) or {}
    # D-66 kod karsiligi: brif yolu panoda yaziliysa diskte de olmali (B-03).
    brief = gorev.get("brief") or ""
    if brief and not (tb.ROOT / brief).exists():
        print(f"HATA: brif diskte yok -> {brief} (D-66). Pano yolunu duzelt veya brifi yaz.")
        return 2
    # B-12: bagimlilik kapanmadiysa uyar, DURDURMA (D-65 is durmaz).
    for bagli in gorev.get("dependencies") or []:
        onceki = tb.gorev_getir(bagli)
        durum = onceki.get("durum") if onceki else "PANODA YOK"
        if durum != "done":
            print(f"UYARI: bagimlilik kapanmadi -> {bagli} (durum: {durum})")
    try:
        sonuc = trigger.tetik_al(args.ajan, args.task_id)
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"ALINDI: {sonuc['task_id']} -> {args.ajan} (durum: aktif)")
    return 0


def _hafiza_hedefleri(task_id: str) -> list[Path]:
    """B-14: izin aranacagi dosyalar — SSOT + brief'te adi gecen hub'lar.

    Brief `hubs/XXX` yazmiyorsa varsayilan `_HUB` kullanilir; boylece eski
    brief'ler de kapiya takilir ama nereye yazilacagi belirsiz kalmaz.
    """
    gorev = tb.gorev_getir(task_id) or {}
    hublar: list[Path] = []
    brief = str(gorev.get("brief") or "")
    by = (_KOK / brief) if brief else None
    if by is not None and by.exists():
        metin = by.read_text(encoding="utf-8", errors="replace")
        for ad in re.findall(r"hubs/([A-Za-z0-9_\-]+)", metin):
            yol = _KOK / "hubs" / f"{ad}.md"
            if yol.exists() and yol not in hublar:
                hublar.append(yol)
    return [_SSOT] + (hublar or [_HUB])


def _hafiza_izi(task_id: str) -> list[Path]:
    """task_id'nin izini birakan dosyalar; bos liste = hicbir yerde gecmiyor."""
    return [y for y in _hafiza_hedefleri(task_id)
            if y.exists() and task_id in y.read_text(encoding="utf-8", errors="replace")]


def cmd_teslim(args: argparse.Namespace) -> int:
    # B-14 kapisi: kapanan is SSOT ya da hub'da iz birakmadan teslim edilemez.
    zorla = getattr(args, "zorla", False)
    if not zorla and not _hafiza_izi(args.task_id):
        hedef = _hafiza_hedefleri(args.task_id)[-1]
        print(f"HATA: {args.task_id} hafiza izi yok — teslim reddedildi (B-14).",
              file=sys.stderr)
        print(f"       Yaz: {hedef.relative_to(_KOK).as_posix()} "
              f"\"Kapanan isler\" bolumune {args.task_id} satiri; ya da --zorla.",
              file=sys.stderr)
        return 1

    # D-210 KAPISI 2: teslim oncesi acik sorular var mi?
    # D-336 (ORCH-KIMLIK-ZINCIRI-01): ajan-chat.jsonl (chat.teslim_kontrol_et)
    # TEK BASINA yeterli degil — chat_gonder.py yazdigi messages.jsonl'de
    # cevapsiz mesaj varsa bu kapi onu GORMUYORDU. Ikisi birlikte kontrol edilir.
    engeller = chat.teslim_kontrol_et(args.task_id)
    mesaj_nedenleri = _mesaj_kontrol_et(args.task_id, args.ajan)
    if engeller["engel"] or mesaj_nedenleri:
        print(f"[D-210 TESLIM KAPISI] HATA: Acik sorular var — teslim reddedildi.",
              file=sys.stderr)
        for neden in engeller["nedenler"] + mesaj_nedenleri:
            print(f"  - {neden}", file=sys.stderr)
        print(f"\nSoruları kapadiğinda teslim yeniden calistir.",
              file=sys.stderr)
        return 1

    # D-318 KAPISI: bulgu defteri kanonik dokuman; teslimden once doldurulur.
    # D-239 deseni: kural gövdesi tek yerde (bulgu_defteri.py), bu komut onu
    # çağırır. Ölçüm: 123 teslim raporunun yalnız 25'inde bulgu bölümü vardı;
    # kural yazılıydı, zorlayıcı yoktu.
    if not bulgu.task_var_mi(args.task_id):
        print("[D-318 BULGU KAPISI] HATA: bulgu defterinde bu görev kaydi yok — "
              "teslim reddedildi.", file=sys.stderr)
        print(f"       Defter: {bulgu.DEFLER.as_posix()} (tek kanonik dosya)", file=sys.stderr)
        print(f"       Once bulgunu yaz, sonra teslim et:", file=sys.stderr)
        print(f"       python scripts/bulgu_defteri.py ekle "
              f"--task-id {args.task_id} --rol {args.ajan} \\", file=sys.stderr)
        print("         --ozet \"...\" --karar \"D-NNN | kapandi:<kanit>\" "
              "--renk oneri|dikkat|acil|tamam", file=sys.stderr)
        print("       Bulgun yoksa: --ozet \"bulgu yok, nedeni\" "
              "--karar \"red: <gerekce>\"", file=sys.stderr)
        return 1

    # D-321 KAPISI: hub/rapor satirindaki task_id ile board'daki task_id
    # birebir eslesmeli (SKOR/SCOR gibi yazim sapmalarini teslim oncesi yakalar).
    if tb.gorev_getir(args.task_id) is None:
        print(f"[D-321 BOARD KAPISI] HATA: {args.task_id} task_board.json'da "
              f"birebir bulunamadi — teslim reddedildi.", file=sys.stderr)
        print("       Yazim sapmasi olabilir (orn. SKOR/SCOR); gorev_getir ile "
              "panoda gecerli task_id'yi dogrula.", file=sys.stderr)
        return 1

    try:
        sonuc = trigger.teslim_et(
            args.task_id, args.ajan, args.ozet, _ayristir_liste(args.cikti)
        )
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"TESLIM: {sonuc['task_id']} -> durum: review (onay bekliyor)")
    print("       Onaysiz done OLMAZ; kontrolor onayi sonrasi tamamlanir.")
    # D-312: teslim bitis degil, dongunun bir turu. Durmak yasak.
    # D-335: tek komut — is gelene kadar bekler, gelince ne yapilacagini basar.
    print(f"\n[D-312] SIRADAKI ADIM ZORUNLU — durma, insan bekleme:")
    print(f"  nobet: python scripts/gorev_kutusu.py nobet --ajan {args.ajan}")
    print(f"         (posta + chat is gelene kadar bekler; cikis 0 = IS VAR, hemen yap)")
    if zorla and not _hafiza_izi(args.task_id):
        tb.gorev_guncelle(args.task_id, hafiza_izi="atlandi")
        print("       UYARI: --zorla ile gecildi; panoya hafiza_izi=atlandi islendi (D-65).")
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

    # D-329: onay tek basina tetik URETMEZ; is bitince kuyruk bosalir ama
    # yerine yeni tetik dusmez. Bu yuzden onayin ardindan tetik dengesi
    # tetiklenir. Hata olursa ONAY BOZULMAZ (D-260: asil is onay).
    try:
        dusen = _tetik_dengele(kuru=False, sessiz=False)
        if dusen:
            print(f"DENGE: bos kuyruga tetik dustu -> {', '.join(dusen)}")
        else:
            print("DENGE: tetik dusecek bos kuyruk yok")
    except Exception as exc:                  # noqa: BLE001
        print(f"[denge] atlandi: {type(exc).__name__}: {exc}", file=sys.stderr)
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
    D-210 kapisi: acik sorular varsa, teslim engelleyiciye basvur.
    """
    # D-198 kapisi: bozuk panoyla zincire girilmez (kod 2 = dur, 1 = uyarip devam).
    if not getattr(args, "simulasyonsuz", False):
        sim = cmd_simulasyon(argparse.Namespace(kuru=True))
        if sim >= 2:
            print("D-198: simulasyon HATA verdi; basla calismadi. Once duzelt "
                  "ya da --simulasyonsuz ile gec.", file=sys.stderr)
            return 2
        if sim == 1:
            print("(simulasyon uyarili; zincir devam ediyor — D-65)\n")
    ajan = args.ajan

    # D-320: oturum basinda commit edilmemis dosya varsa uyar (git_stash_guard.py yerine,
    # hafif versiyon — .git/hooks/pre-commit zaten commit anini koruyor, burada sadece hatirlatma).
    try:
        git_durum = subprocess.run(
            ["git", "status", "--porcelain"], cwd=_KOK, capture_output=True,
            text=True, timeout=5,
        )
        if git_durum.returncode == 0 and git_durum.stdout.strip():
            satirlar = git_durum.stdout.strip().splitlines()
            print(f"\n[D-320 GIT UYARISI] {len(satirlar)} commit edilmemis dosya var:")
            for s in satirlar[:5]:
                print(f"  {s}")
            if len(satirlar) > 5:
                print(f"  ... ve {len(satirlar) - 5} dosya daha")
            print("  Onceki oturumdan kalmis olabilir — once incele, gerekirse commit et.\n")
    except Exception:
        pass  # git yoksa veya zaman asimi olursa basla akisini durdurma

    # D-210 KAPISI 1: basla oncesi acik sorular var mi?
    # D-336: ajan-chat.jsonl + messages.jsonl birlikte (ORCH-KIMLIK-ZINCIRI-01).
    acik_sorunlar = chat.ajan_acik_sorulari(ajan)
    acik_mesajlar = _chat_yeni_mesajlar(ajan, "")
    if acik_sorunlar or acik_mesajlar:
        print(f"\n[D-210 BASLA KAPISI] ACIK SORULAR — cevapla, sonra basla yeniden calistir:")
        i = 0
        for i, s in enumerate(acik_sorunlar, 1):
            print(f"  {i}. {s['task_id']}: {s['sorun']}")
            print(f"     (kimden: {s['kimden']}, onem: {s.get('onem', 'orta')})")
        for j, m in enumerate(acik_mesajlar, i + 1):
            print(f"  {j}. {m.get('task_id') or '-'}: {str(m.get('mesaj', ''))[:120]}")
            print(f"     (kimden: {m.get('kimden', '?')}, kaynak: chat_gonder)")
        toplam = len(acik_sorunlar) + len(acik_mesajlar)
        print(f"\nToplam {toplam} acik soru. Soruları cevapladiğinda:")
        print(f"  python scripts/gorev_kutusu.py basla --ajan {ajan}")
        print()
        return 0

    bekleyen = trigger.bekleyen_tetikler(ajan)
    kalan = trigger.zincir_kalan(ajan)
    rol = trigger.AJAN_ROLU.get(ajan, "uretim")
    print(f"=== {trigger.ajan_goster(ajan)} OTONOM ZINCIR ===")
    if not bekleyen and not kalan:
        # D-312: posta bos olmak durma sebebi degil. D-335: nobet komutu is gelene kadar bekler.
        print("Posta bos, zincir yok — ama DURMA (D-312).")
        print(f"  simdi: python scripts/gorev_kutusu.py nobet --ajan {ajan}")
        print("         (is gelene kadar bekler; cikis 0 = IS VAR -> listeyi yap, sonra yine nobet)")
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
  5) posta + chat kontrol (D-312, ZORUNLU — atlanmaz):
       python scripts/gorev_kutusu.py bak --ajan {ajan}
       python scripts/ajan_chat.py oku --son 10
     -> mesaj varsa CEVAPLA, yeni gorev varsa AL ve 1. adima don.
ZINCIR BITINCE (tum gorevler teslim):
  6) toplu raporu yaz: {rapor}
  7) postala: python scripts/gorev_kutusu.py rapor-postala --ajan {ajan} \\
       --rapor "{rapor}" --baslik "zincir bitti: {len(sira)} gorev"
  8) DURMA: python scripts/gorev_kutusu.py basla --ajan {ajan} ile yeniden yokla (D-312).
Arada KAHIN'e soru sorma; blokaj varsa raporda yaz.""")
    return 0


def _mesaj_kontrol_et(task_id: str, ajan: str) -> list[str]:
    """messages.jsonl: `ajan`a gelen, task_id'ye bagli CEVAPSIZ mesaj var mi.

    D-336 / ORCH-KIMLIK-ZINCIRI-01: chat.teslim_kontrol_et() yalnizca
    ajan-chat.jsonl'yi okur; chat_gonder.py'nin yazdigi messages.jsonl'yi
    gormuyordu. Bu yuzden bazi teslimler "acik soru var" diye reddedildi
    halbuki cevap messages.jsonl'deydi (ya da hic cevap yoktu, kapi bunu
    gormemisti). Ikisi artik birlikte kontrol edilir.

    D-210 (duzeltme): onceki imza yalniz task_id aliyordu ve mesajin
    YONU bakilmadan her cevapsiz kayit engel sayiliyordu. Boylece ajanin
    baskalarina gonderdigi rapor (ihsan -> yasu) kendi teslimini blokeliyordu
    ve cevapsiz soru ile cevap beklemeyen bildirim ayirt edilemiyordu.
    Simdi yon filtresi var: yalniz `ajan`a gelen (kime == ajan veya "hepsi")
    ve `ajan`in kendi gondermedigi mesajlar engeldir.

    `sonra` verilirse (nobet) yalniz o tarihten yeniler sayilir.
    """
    ajan = trigger.ajan_normalize(ajan)
    yol = tb.STATE_DIR / "chat" / "messages.jsonl"
    if not yol.exists():
        return []
    nedenler: list[str] = []
    for satir in yol.read_text(encoding="utf-8").splitlines():
        try:
            k = json.loads(satir)
        except json.JSONDecodeError:
            continue
        if k.get("task_id") != task_id or k.get("yanit_alindi"):
            continue
        if k.get("kimden") == ajan:
            continue  # ajanin kendi ciktisi: cevap bekleyen soru degil
        if k.get("kime") not in (ajan, "hepsi"):
            continue  # baska birine gonderilmis: bu ajani bekletmez
        nedenler.append(
            f"{str(k.get('mesaj', ''))[:120]} (kimden: {k.get('kimden', '?')}, chat_gonder)"
        )
    return nedenler


def _chat_yeni_mesajlar(ajan: str, sonra: str) -> list[dict]:
    """messages.jsonl: ajana (veya hepsi) gelen, `sonra` tarihinden yeni, cevapsiz mesajlar."""
    yol = tb.STATE_DIR / "chat" / "messages.jsonl"
    if not yol.exists():
        return []
    cikti: list[dict] = []
    for satir in yol.read_text(encoding="utf-8").splitlines():
        try:
            k = json.loads(satir)
        except json.JSONDecodeError:
            continue
        if (k.get("kime") in (ajan, "hepsi") and k.get("kimden") != ajan
                and not k.get("yanit_alindi") and str(k.get("tarih", "")) > sonra):
            cikti.append(k)
    return cikti


def nobet_turu(ajan: str, sonra: str) -> list[str]:
    """Tek yoklama: posta + acik soru + yeni chat. Bos liste = is yok (D-335)."""
    isler: list[str] = []
    for k in trigger.bekleyen_tetikler(ajan) + trigger.zincir_kalan(ajan):
        isler.append(f"POSTA  {k['task_id']} -> python scripts/gorev_kutusu.py al --ajan {ajan} --task-id {k['task_id']}")
    for s in chat.ajan_acik_sorulari(ajan):
        isler.append(f"SORU   {s['task_id']} ({s['kimden']}): {s['sorun'][:80]} -> ajan_chat.py guncelle")
    for m in _chat_yeni_mesajlar(ajan, sonra):
        isler.append(f"CHAT   {m.get('task_id') or '-'} ({m.get('kimden')}): {str(m.get('mesaj', ''))[:80]} -> chat_gonder.py --to {m.get('kimden')}")
    return isler


def cmd_nobet(args: argparse.Namespace) -> int:
    """D-335: is gelene kadar bekle. Cikis 0 = IS VAR (liste basildi), 3 = azami sure doldu.

    Ajan teslimden sonra bunu calistirir; komut donmeden 'bitti' diyemez.
    ponytail: tek surec, dosya yoklama; event/websocket gerekirse buraya takilir.
    """
    import time
    ajan = trigger.ajan_normalize(args.ajan)
    sonra = trigger._simdi()
    azami = args.azami_dk * 60
    baslangic = time.monotonic()
    tur = 0
    while True:
        tur += 1
        isler = nobet_turu(ajan, sonra)
        if isler:
            print(f"[NOBET {ajan}] tur {tur}: {len(isler)} IS VAR — simdi yap, sonra yine nobet:")
            for i in isler:
                print(f"  {i}")
            return 0
        gecen = int(time.monotonic() - baslangic)
        print(f"[NOBET {ajan}] tur {tur} bos ({gecen}s). {args.bekle}s sonra yine bakacagim.", flush=True)
        if tur == 3:
            print(f"  3 tur bos: orkestratore kisa rapor at (chat_gonder.py --to ihsan --kimden {ajan} "
                  f"--type rapor --mesaj \"nobet: 3 tur bos\"), beklemeye devam.")
        if gecen + args.bekle > azami:
            print(f"[NOBET {ajan}] azami {args.azami_dk} dk doldu, is yok. Yeniden: "
                  f"python scripts/gorev_kutusu.py nobet --ajan {ajan}")
            return 3
        time.sleep(args.bekle)


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


def _yedek_sayimi() -> list[str]:
    """AGENTS.md 'son 3 yedek' politikasinin makine karsiligi (B-15)."""
    yedekler = sorted(
        p for p in tb.STATE_DIR.iterdir()
        if p.is_file() and ("yedek" in p.name or "backup" in p.name) and "task_board" in p.name
    )
    if len(yedekler) <= 3:
        return []
    fazla = yedekler[:-3]
    return [f"{len(yedekler)} pano yedegi var (politika: son 3). Silinebilir: "
            + ", ".join(p.name for p in fazla)]


def cmd_bakim(args: argparse.Namespace) -> int:
    """Pano hijyeni: cift kayit, takili tetik, bayat zincir, blokaj otomasyonu."""
    if args.rapor:
        t = duzen.pano_tarama()
        print("[TARAMA] (dokunulmadi)")
        print(f"  cift kayit: {t['cift_kayit'] or 'yok'}")
        # D-198: arsiv de mukerrer kapisidir (salt okunur tarama).
        for s in t["arsiv_cakisma"]:
            print(f"  arsiv cakismasi: {s}")
        if not t["arsiv_cakisma"]:
            print("  arsiv cakismasi: yok")
        for s in t["takili_tetik"]:
            print(f"  takili: {s}")
        if not t["takili_tetik"]:
            print("  takili tetik: yok")
        print(f"  blocked: {', '.join(t['blocked']) or 'yok'}")
        for s in _yedek_sayimi():
            print(f"  UYARI: {s}")
        return 0
    r = duzen.pano_bakim()
    print("[BAKIM] uygulandi:")
    print(f"  dedupe: {r['dedupe']} | tetik esit: {r['tetik_esit']}")
    for z in r["zincir"]:
        print(f"  zincir: {z}")
    print(f"  blokaj acilan: {', '.join(r['acilan']) or 'yok'}")
    print(f"  blokaj kapanan: {', '.join(r['kapanan']) or 'yok'}")
    for s in _yedek_sayimi():
        print(f"  UYARI: {s}")
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


# --- simulasyon kapisi (D-198) -------------------------------------------
# Rapor ayri bir scripts/ssot_durum_denetim.py onerdi; acilmadi. Ayri betik
# bugun bir dosya, alti ay sonra data/_tmp mezarligi (B-15 bunun kaniti).
# Kontroller zaten panoyu/tetigi okuyan bu komutun icinde yasiyor.
_SSOT = _KOK / "AI proje v1" / "V10" / "05_versiyonlar" / "02_admin_panel_hedef_dokumani.md"
_HUB = _KOK / "hubs" / "ADMIN_DASHBOARD_HUB.md"
_PLANS = _KOK / "plans"
_SABLON_BASLIKLAR = ("## Neden", "## Doğrulanacak varsayım", "## Adımlar", "## Kabul kriteri")

# B-14 hafiza kapisi bu tarihte yururluge girdi. Once kapanan 376 is tek tek
# SSOT/hub'a yazilmaz; onlarin karsiligi hub'lardaki arsiv ozeti satirlaridir
# (D-186 wikilink). Bu tarih ve sonrasinda kapanan her is iz birakmak zorunda.
HAFIZA_KAPISI_YURURLUK = "2026-09-24"


def _kontrol_yaz(no: int, ad: str, seviye: str, bulgular: list[str],
                 ornek: bool = True, limit: int = 5) -> int:
    """Tek kontrolun ciktisini basar, katki kodunu doner (0/1/2)."""
    if not bulgular:
        print(f"{no}. {ad}: OK")
        return 0
    print(f"{no}. {ad}: {seviye} {len(bulgular)} adet")
    if ornek:
        for b in bulgular[:limit]:
            print(f"     - {b}")
        if len(bulgular) > limit:
            print(f"     ... +{len(bulgular) - limit} daha")
    return 2 if seviye == "HATA" else 1


def _atlandi(no: int, ad: str, gerekce: str) -> int:
    """Uygulanamayan kontrol uydurma OK yazmaz (urun sahibi kurali)."""
    print(f"{no}. {ad}: ATLANDI: {gerekce}")
    # YA-02: atlanmak hata degil (kod 2) ama sessiz de degil -- denetlenmemis
    # ortam D-198 kapisindan temiz diye gecmesin. Kod hesabi: max(kodlar).
    return 1


def cmd_simulasyon(args: argparse.Namespace) -> int:
    """D-198: her uretim/planlama turu oncesi zorunlu, salt okunur kapi."""
    ornek = not args.kuru
    pano = tb.gorev_listesi()
    acik = [t for t in pano
            if t.get("durum") not in tb.KAPALI_DURUMLAR and t.get("durum") != "yedek"]
    kodlar: list[int] = []
    print("=== SIMULASYON (salt okunur; hicbir dosyaya yazilmaz) ===")

    # 1 — B-01: arsivde kapanmis is panoya ikinci kez girmis mi.
    # Yalniz ACIK gorev sayilir: kapanmis gorevin hem panoda hem arsivde
    # durmasi "arsivle henuz kosmamis" demektir, cakisma degil (2026-10-03:
    # 105 sahte HATA tum ajanlari kilitledi; arsivle idempotent, kopya yazmaz).
    bulgular = []
    for t in acik:
        yer = tb.arsivde_bul(t["task_id"])
        if yer:
            bulgular.append(f"{t['task_id']} -> {yer}")
    kodlar.append(_kontrol_yaz(1, "Pano<->arsiv task_id cakismasi (B-01)", "HATA", bulgular, ornek))

    # 2 — B-03: brifsiz atama yasak (D-66) kapisinin diskteki karsiligi.
    bulgular = []
    for t in acik:
        b = t.get("brief")
        if not b:
            bulgular.append(f"{t['task_id']}: brief alani bos")
        elif not (_KOK / b).exists() and not Path(b).exists():
            bulgular.append(f"{t['task_id']}: {b} diskte yok")
    kodlar.append(_kontrol_yaz(2, "Brief dosyasi diskte var mi (B-03)", "HATA", bulgular, ornek))

    # 3 — B-04: kilitli dosya panoda yazili mi.
    bulgular = [t["task_id"] for t in acik if not t.get("dosyalar")]
    kodlar.append(_kontrol_yaz(3, "Acik gorevde dosyalar bos mu (B-04)", "UYARI", bulgular, ornek))

    # 4 — B-12: bagimlilik kaydi var mi, kapandi mi. Uyari; is durmaz (D-65).
    # Acik bir gorevin bagimliligi da acik olmasi BEKLENEN haldir; sira boyle
    # kurulur, uyari degildir. Yalniz KIRIK bagimlilik -- ne panoda ne arsivde
    # bulunan bir task_id -- gercek kayip isarettir.
    bilinen = {t["task_id"] for t in pano}
    bulgular = []
    for t in acik:
        for d in t.get("dependencies") or []:
            if d not in bilinen and not tb.arsivde_bul(d):
                bulgular.append(f"{t['task_id']} <- {d} (hicbir yerde kayit yok)")
    kodlar.append(_kontrol_yaz(4, "Kirik bagimlilik kaydi (B-12)", "UYARI", bulgular, ornek))

    # 5 + 6 — D-197 kural 5 (yuzde yasak) ve kural 1-2 (durum yalniz §7'de).
    if not _SSOT.exists():
        kodlar.append(_atlandi(5, "SSOT yuzde satiri (D-197 k.5)", f"{_SSOT.name} diskte yok"))
        kodlar.append(_atlandi(6, "SSOT 8-12 durum/oncelik etiketi (D-197 k.1-2)",
                               f"{_SSOT.name} diskte yok"))
        ssot_metin = ""
    else:
        ssot_metin = _SSOT.read_text(encoding="utf-8", errors="replace")
        yuzde, etiket = [], []
        bolum = 0
        for i, s in enumerate(ssot_metin.splitlines(), 1):
            m = re.match(r"^#{2,4} (\d+)", s)
            if m:
                bolum = int(m.group(1))
            if bolum != 14 and re.search(r"\d\s*%", s):
                yuzde.append(f"{_SSOT.name}:{i}  {s.strip()[:70]}")
            if bolum in (8, 9, 10, 11, 12) and re.search(r"✅|⬜|\bP[012]\b", s):
                etiket.append(f"{_SSOT.name}:{i}  {s.strip()[:70]}")
        kodlar.append(_kontrol_yaz(5, "SSOT yuzde satiri (D-197 k.5, 14 harici)",
                                   "UYARI", yuzde, ornek))
        kodlar.append(_kontrol_yaz(6, "SSOT 8-12 durum/oncelik etiketi (D-197 k.1-2)",
                                   "UYARI", etiket, ornek))

    # 7 — B-17: brief'ler _brief_sablon.md baslik yapisina uyuyor mu.
    # Kapsam AKTIF PANODAKI gorevlerin brief'leridir. plans/ altinda kapanmis
    # islerden kalan onlarca brief duruyor; onlari bugunun sablonuna cekmek
    # gecmisi yeniden yazmaktir, is uretmez. Denetlenen sey calisilan istir.
    briefler: list[Path] = []
    for t in acik:
        ad = t.get("brief")
        if not ad:
            continue
        p = _KOK / ad
        if not p.exists():
            p = Path(ad)
        if p.exists() and p not in briefler:
            briefler.append(p)
    if not briefler:
        kodlar.append(_atlandi(7, "Aktif brief sablon uyumu (B-17)",
                               "aktif panoda diskte duran brief yok"))
    else:
        bulgular = []
        for b in briefler:
            metin = b.read_text(encoding="utf-8", errors="replace")
            yok = [h for h in _SABLON_BASLIKLAR if h not in metin]
            if yok:
                bulgular.append(f"plans/{b.name}:1  eksik baslik: {', '.join(yok)}")
        kodlar.append(_kontrol_yaz(7, "Aktif brief sablon uyumu (B-17)", "UYARI", bulgular, ornek))

    # 8 — B-14: kapanan is SSOT veya hub'da task_id izi birakmis mi.
    # Aktif pano + son ceyregin arsivi birlikte taranir: arsivlenen is gozden
    # kaybolmasin diye (D-198). Daha eski ceyrekler tarihtir, gurultu yapar.
    # Yururluk esigi: bitis tarihi HAFIZA_KAPISI_YURURLUK oncesi olan kayitlar
    # gecmis borcudur, hub arsiv ozetiyle kapandi; tek tek denetlenmez.
    kapanan = [t for t in pano if t.get("durum") in tb.KAPALI_DURUMLAR]
    arsivler = sorted(tb.STATE_DIR.glob("task_board_arsiv_*.json")) if tb.STATE_DIR.is_dir() else []
    if arsivler:
        kapanan += [t for t in tb._read_json(arsivler[-1])
                    if t.get("durum") in tb.KAPALI_DURUMLAR]
    # bitis bos/None ise kayit esikten once kapanmistir (alan sonradan eklendi);
    # metin karsilastirmasi "None" >= "2026-.." tuzagina dusmesin diye acik kontrol.
    def _esik_sonrasi(t: dict) -> bool:
        b = t.get("bitis")
        return bool(b) and str(b)[:10] >= HAFIZA_KAPISI_YURURLUK

    kapanan = [t for t in kapanan if _esik_sonrasi(t)]
    # Iz her hub'da birakilabilir (_hafiza_hedefleri brief'teki `hubs/XXX`
    # satirini okur), o yuzden kapi tek hub'a degil hubs/ dizininin tamamina bakar.
    _hub_dizin = _HUB.parent
    hub_metin = "".join(
        h.read_text(encoding="utf-8", errors="replace")
        for h in sorted(_hub_dizin.glob("*.md"))
    ) if _hub_dizin.is_dir() else ""
    if not kapanan:
        kodlar.append(_atlandi(8, "Kapanan gorevin SSOT/hub izi (B-14)",
                               f"{HAFIZA_KAPISI_YURURLUK} ve sonrasinda kapanmis gorev yok"))
    elif not ssot_metin and not hub_metin:
        kodlar.append(_atlandi(8, "Kapanan gorevin SSOT/hub izi (B-14)",
                               "SSOT ve hub dosyasi diskte yok"))
    else:
        gorulen: set[str] = set()
        bulgular = []
        for t in kapanan:
            tid = str(t.get("task_id") or "")
            if not tid or tid in gorulen:
                continue
            gorulen.add(tid)
            if tid not in ssot_metin and tid not in hub_metin:
                bulgular.append(f"{tid}: ne SSOT'ta ne hub'da gecmiyor")
        kodlar.append(_kontrol_yaz(8, "Kapanan gorevin SSOT/hub izi (B-14)",
                                   "UYARI", bulgular, ornek, limit=10))

    kod = max(kodlar)
    print(f"\nSONUC: cikis kodu {kod}  (0 temiz / 1 uyari / 2 hata)")
    if kod:
        print("D-198: cikti temiz degilse uretim/planlama turu baslamaz.")
    return kod


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


AJANLAR_TUM = ("yasu", "utku", "ihsan", "salih")
ONCELIK_SIRA = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def _tetik_dengele(kuru: bool = False, sessiz: bool = False) -> list:
    """Bos tetik kuyrugu olan ajanin plan isine tetik dusurur.

    Neden ayri yardimci: hem `denge` komutu hem `onayla` ayni kurali
    uygular; iki kopyasi olursa biri guncellenip digeri eskir.

    KURAL (D-68 ruhu): yalniz `plan` durumunda ve kuyrugu bos olan
    ajanlara. Aktif/review gorevlere, dolu kuyruklara ve zaten tetikli
    gorevlere DOKUNULMAZ. Bu dagitimdir, gorev transferi DEGILDIR -
    sahiplik degismez.

    D-DENGE-TARIH-BAGIMLILIK-01 (2026-10-04): `baslangic` gelecekte olan
    veya `dependencies` icinde henuz `done` olmayan bir is varsa, ajanin
    kuyrugu bos olsa da tetik dusurulmez. Eskiden bu kontrol yoktu; plan
    isleri gunler/hafta once tetiklenip yuzlerce UYARI biriktiriyordu
    (olcum: SCRAPE-006/007, 2026-10-04 — bkz. AGENTS.md karar kaydi).
    """
    def bekleyen(ajan: str) -> list:
        try:
            return [k for k in trigger._tetikleri_oku(ajan) if k["durum"] == "bekliyor"]
        except Exception:
            return []

    bugun = date.today().isoformat()
    durumlar = {g.get("task_id"): g.get("durum") for g in tb.gorev_listesi()}

    def hazir_mi(g: dict) -> bool:
        baslangic = str(g.get("baslangic") or "")[:10]
        if baslangic and baslangic > bugun:
            return False                  # gelecek tarihli is, henuz sira gelmedi
        for dep in g.get("dependencies") or []:
            if durumlar.get(dep) != "done":
                return False              # bagimlilik bitmemis
        return True

    ts = [g for g in tb.gorev_listesi()
          if g.get("durum") == "plan" and g.get("sahip") in AJANLAR_TUM
          and hazir_mi(g)]
    kuyruk = {a: len(bekleyen(a)) for a in AJANLAR_TUM}

    adaylar: list = []
    for a in AJANLAR_TUM:
        if kuyruk[a] > 0:
            continue                      # kuyrugu dolu -> dokunma
        for g in ts:
            if g.get("sahip") != a:
                continue
            if any(k["task_id"] == g.get("task_id") for k in bekleyen(a)):
                continue                  # zaten tetikli
            adaylar.append(g)
    adaylar.sort(key=lambda g: (ONCELIK_SIRA.get(g.get("oncelik"), 9),
                                g.get("task_id", "")))

    # AJAN BASINA EN FAZLA 1 TETIK (olcum): kuyrugu bos olan her ajana
    # butun plan isleri tek seferde dusulurse kuyruk yeniden birikir ve
    # denge yine bozulur. Kuyruk bos olan ajan ISE ALIR, bos kalir.
    secilen = []
    alinan = set()
    for g in adaylar:
        a = g.get("sahip")
        if a in alinan:
            continue
        secilen.append(g)
        alinan.add(a)

    if kuru:
        return secilen

    dusen = []
    for g in adaylar:
        try:
            trigger.tetik_ekle(g.get("task_id"), g.get("sahip"),
                               "DENGE: kuyrugu bos olan ajana tetik dusruldu.")
            dusen.append(g.get("task_id"))
        except Exception as exc:          # noqa: BLE001
            if not sessiz:
                print(f"   [denge] tetik duseMEDI {g.get('task_id')}: {exc}",
                      file=sys.stderr)
    if dusen and not sessiz:
        print("DENGE tetik dusen: " + ", ".join(dusen))
    return dusen


def cmd_denge(args: argparse.Namespace) -> int:
    """Tetik kuyrugunu dengeler (bos kuyruga plan isi tetikler).

    Kural `_tetik_dengele` icinde; bu komut yalniz raporlar ve uygular.
    --kuru ile hicbir sey yazmadan once/sonra gorulur.
    """
    once = {}
    for a in AJANLAR_TUM:
        try:
            once[a] = len([k for k in trigger._tetikleri_oku(a)
                           if k["durum"] == "bekliyor"])
        except Exception:
            once[a] = 0
    print("== TETIK KUYRUKLARI (once) ==")
    for a in AJANLAR_TUM:
        print(f"   {a:<7} {once[a]}")

    adaylar = _tetik_dengele(kuru=True)
    print()
    print("== TETIK DUSELECEK ADAMLAR ==")
    if not adaylar:
        print("   (yok: butun ajanlarin kuyrugu dolu veya plan isi yok)")
    for g in adaylar:
        print(f"   {g.get('task_id')} -> {g.get('sahip')} ({g.get('oncelik')})")

    if args.kuru:
        print()
        print("KURU: hicbir sey yazilmadi.")
        return 0

    _tetik_dengele(kuru=False)

    print()
    print("== TETIK KUYRUKLARI (sonra) ==")
    for a in AJANLAR_TUM:
        try:
            n = len([k for k in trigger._tetikleri_oku(a) if k["durum"] == "bekliyor"])
        except Exception:
            n = 0
        print(f"   {a:<7} {once[a]} -> {n}")
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


def cmd_ekle(args: argparse.Namespace) -> int:
    """BORC-GOREV-EKLE-01: Panoya gorev ekle (elle JSON duzenleme yerine)."""
    try:
        gorev = tb.gorev_ekle(
            args.task_id, args.baslik, args.sahip, args.oncelik,
            dosyalar=_ayristir_liste(args.dosyalar),
            brief=args.brief or None, talimat=args.talimat or None,
            mod=args.mod,
        )
    except ValueError as exc:
        return _hata(exc)
    print(f"EKLENDI: {gorev['task_id']} -> {gorev['sahip']} ({gorev['oncelik']})")
    if args.tetikle:
        try:
            trigger.tetik_ekle(args.task_id, args.sahip, args.talimat or "")
            print(f"  -> tetiklendi: {args.sahip}")
        except trigger.TriggerError as exc:
            print(f"  UYARI: tetik atilamadi ({exc})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ORCH-08 — Ajan posta kutusu + kontrolör onay")

    sub = parser.add_subparsers(dest="komut", required=True)

    bak_p = sub.add_parser("bak", help="Ajanın posta kutusunu göster")
    bak_p.add_argument("--ajan", required=True, help="Ajan adı (kilo, roo, vs.)")
    bak_p.set_defaults(func=cmd_bak)

    basla_p = sub.add_parser("basla", help="Tek kelime tetik: posta+zincir+otonom talimat")
    basla_p.add_argument("--ajan", required=True)
    basla_p.add_argument("--simulasyonsuz", action="store_true",
                         help="D-198 simulasyon kapisini atla (kacis kapisi, D-65)")
    basla_p.set_defaults(func=cmd_basla)

    nobet_p = sub.add_parser("nobet", help="D-335: is gelene kadar bekle (posta+soru+chat); cikis 0 = IS VAR")
    nobet_p.add_argument("--ajan", required=True)
    nobet_p.add_argument("--bekle", type=int, default=120, help="Turlar arasi saniye (varsayilan 120)")
    nobet_p.add_argument("--azami-dk", type=int, default=60, help="Bos beklemenin ust siniri, dakika (cikis 3)")
    nobet_p.set_defaults(func=cmd_nobet)

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
    teslim_p.add_argument("--zorla", action="store_true",
                          help="Hafiza izi olmadan teslim et (panoya hafiza_izi=atlandi islenir)")
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

    simulasyon_p = sub.add_parser("simulasyon", help="D-198: tur oncesi zorunlu salt okunur kapi")
    simulasyon_p.add_argument("--kuru", action="store_true",
                              help="Ornek satirlari bastirma, sadece sayi + cikis kodu")
    simulasyon_p.set_defaults(func=cmd_simulasyon)

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
    denge_p = sub.add_parser("denge", help="Tetik kuyrugunu dengele (bos kuyruga plan isi)")
    denge_p.add_argument("--kuru", action="store_true", help="Sadece raporla, yazma")
    denge_p.set_defaults(func=cmd_denge)

    ekle_p = sub.add_parser("ekle", help="BORC-GOREV-EKLE-01: Panoya gorev ekle")
    ekle_p.add_argument("--task-id", required=True)
    ekle_p.add_argument("--baslik", required=True)
    ekle_p.add_argument("--sahip", required=True, help="Atanacak ajan")
    ekle_p.add_argument("--oncelik", default="P1")
    ekle_p.add_argument("--dosyalar", default="", help="Virgülle ayrılmış kilitli dosyalar")
    ekle_p.add_argument("--brief", default="", help="Brif dosya yolu (D-66)")
    ekle_p.add_argument("--talimat", default="", help="Görev talimatı (D-80)")
    ekle_p.add_argument("--mod", default="code", choices=["code", "architect"])
    ekle_p.add_argument("--tetikle", action="store_true", help="Ekle + sahibe hemen tetikle")
    ekle_p.set_defaults(func=cmd_ekle)

    args = parser.parse_args()
    # D-33 ajan adı kuralı: "Ajan kilo" / "Kilo" / "kilo_code" → "kilo".
    # Tüm alt komutlar tek noktadan kanonik ada çevrilir.
    for alan in ("ajan", "yeni_ajan", "hedef", "sahip"):
        deger = getattr(args, alan, None)
        if deger:
            try:
                setattr(args, alan, trigger.ajan_normalize(deger))
            except trigger.TriggerError as exc:
                return _hata(exc)
    sonuc = args.func(args)
    if args.komut not in SALT_OKUR_KOMUTLAR:
        _notion_senkron()
    return sonuc


# 2026-10-03 olcum (cProfile): `bak` 14.7 s, bunun 14.66 s'si _notion_senkron (10 HTTP + 4 s sleep).
# Pano degismeyen komutta senkron anlamsiz; 4 ajan x nobet turu = makine donmasi (sahip sikayeti).
SALT_OKUR_KOMUTLAR = frozenset({
    "bak", "nobet", "onay-bekleyen", "raporlar", "ozet", "yardim", "simulasyon", "basla",
})


def _notion_senkron() -> None:
    """Gorev durumu degistiginde Notion panosunu gunceller.

    NEDEN BURADA: pano her komutta elle guncellenmezse 2 saat sonra bayatlar
    ve bakan kisi yanlis bilgi gorur (D-260: kanitsiz durum beyani yasak).

    NEDEN SESSIZ: Notion cokerse asil is (gorev yonetimi) durmamali. Hata
    yazilir, pano eski kalir; ajanlar calismaya devam eder.

    NEDEN TEK YONLU: buradan sadece OKUMA + Notion'a yazim. Notion'dan
    panoya geri yazim YOK.
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from notion_senkron import senkron
        senkron()
    except SystemExit as exc:
        print(f"[NOTION SENKRON] atlandi: {str(exc)[:80]}", file=sys.stderr)
    except ImportError:
        pass          # notion_senkron.py yoksa pano kurulmamistir
    except Exception as exc:                      # noqa: BLE001
        print(f"[NOTION SENKRON] hata: {type(exc).__name__}: {str(exc)[:90]}",
              file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
