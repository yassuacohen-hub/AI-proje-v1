# -*- coding: utf-8 -*-
"""ORCH-10: Pano tutarlılık denetimi + otomatik senkronizasyon.

Akış:
    task_board.json + onay_kuyrugu.json oku
      -> uyumsuzluk taraması (orphan / stuck / alan tutarsızlığı)
      -> trigger.py göreli ithalat regresyon kontrolü
      -> (--uygula) durum normalize + kuyruk sync + archive
      -> sync_report.json yaz
      -> uyumsuzluk kaldıysa exit 1 (CI alarmı)

Kullanım:
    python scripts/pano_denetim.py            # salt-okunur denetim
    python scripts/pano_denetim.py --uygula   # tespit edilenleri düzelt

Saatlik CI: .github/workflows/pano_denetim.yml (cron "0 * * * *").
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.company_master.orchestrator import task_board as tb

# D-186: STATE_DIR kanonik (Huginn Data Insights/data/orchestrator)
# ROOT-göreli yol split üretir; tek kaynak = tb.STATE_DIR
STATE = tb.STATE_DIR
PANO_DOSYA = STATE / "task_board.json"
KUYRUK_DOSYA = STATE / "onay_kuyrugu.json"
RAPOR_DOSYA = STATE / "sync_report.json"
TRIGGER_DOSYA = ROOT / "src" / "company_master" / "orchestrator" / "trigger.py"

# "iptal" de kapalidir: iptal gorev ne stuck'tir ne acik istir. Eksikligi
# 5 sahte uyari uretiyordu (ADMIN-UX-PROFILMENU-01/MENUTREE-01, KILIT-TEMIZLIK-V10-01).
# ALTYAPI-DURUM-SOZLUK-01: artik kopya tutulmuyor, tek kaynak task_board.
KAPALI_DURUMLAR = tb.KAPALI_DURUMLAR
STUCK_ESIK = timedelta(hours=24)
# ponytail: arşiv eşiği sabit; ayarlanabilir olmasına ihtiyaç doğarsa CLI bayrağı ekle.
ARSIV_ESIK = timedelta(days=7)


def _json_oku(yol: Path) -> list[dict]:
    if not yol.exists():
        return []
    return json.loads(yol.read_text(encoding="utf-8-sig"))


def _son_hareket(gorev: dict) -> datetime | None:
    """Görevin en geç zaman damgası (bitis / atandi_tarihi / baslangic)."""
    en_gec = None
    for alan in ("bitis", "atandi_tarihi", "baslangic"):
        ham = gorev.get(alan)
        if isinstance(ham, list):  # bozuk kayıt: baslangic bazen liste
            ham = ham[0] if ham else None
        if not isinstance(ham, str):
            continue
        try:
            an = datetime.fromisoformat(ham)
        except ValueError:
            continue
        if en_gec is None or an > en_gec:
            en_gec = an
    return en_gec


def _an(ham) -> datetime | None:
    if isinstance(ham, list):
        ham = ham[0] if ham else None
    if not isinstance(ham, str):
        return None
    try:
        return datetime.fromisoformat(ham)
    except ValueError:
        return None


def arsiv_kimlikleri() -> frozenset[str]:
    """D-231: arşivlenmiş task_id kümesi (tek okuma).

    tb.arsivde_bul() her çağrıda tüm arşiv dosyalarını okur; 200 kimlik için
    O(n*m). Denetim bir kez okur, küme olarak taşır.
    """
    kimlikler: set[str] = set()
    for yol in tb.arsiv_dosyalari():
        try:
            kayitlar = json.loads(yol.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        kimlikler.update(str(k.get("task_id")) for k in kayitlar)
    return frozenset(kimlikler)


def tara(pano: list[dict], kuyruk: list[dict], simdi: datetime,
         arsiv: frozenset[str] = frozenset()) -> list[dict]:
    """Uyumsuzlukları bulur. Her bulgu: {tip, seviye, task_id, mesaj, duzeltme}.

    seviye "hata": düzeltilmesi gereken tutarsızlık (CI'yi kırar).
    seviye "uyari": bilgi amaçlı (tarihsel kuyruk kaydı, uzun süren görev).

    `arsiv`: D-231 — arşivlenmiş kimlikler. Arşiv panonun devamıdır, yokluğu
    değil; boş geçilirse eski (arşive kör) davranış sürer.
    """
    bulgular: list[dict] = []
    kimlikler = {g.get("task_id") for g in pano}
    durumlar = {g.get("task_id"): g.get("durum") for g in pano}
    gorevler = {g.get("task_id"): g for g in pano}

    def ekle(tip, seviye, tid, mesaj, duzeltme=None):
        bulgular.append({"tip": tip, "seviye": seviye, "task_id": tid,
                         "mesaj": mesaj, "duzeltme": duzeltme})

    for gorev in pano:
        tid = gorev.get("task_id", "?")
        durum = gorev.get("durum")

        # orphan: var olmayan göreve bağımlılık
        for b_id in gorev.get("blokaj") or []:
            if b_id not in kimlikler:
                ekle("orphan", "hata", tid, f"blokaj '{b_id}' panoda yok")

        # alan tutarsızlığı: bitiş dolu ama kapanmamış
        if gorev.get("bitis") and durum not in KAPALI_DURUMLAR:
            ekle("alan", "hata", tid, f"bitis={gorev['bitis']} ama durum={durum}",
                 "bitis_temizle")

        # blocked ama tüm blokajlar kapalı
        if durum == "blocked":
            blokajlar = gorev.get("blokaj") or []
            if blokajlar and all(durumlar.get(b) in KAPALI_DURUMLAR for b in blokajlar):
                ekle("normalize", "hata", tid, "blokajlar kapandı, durum hâlâ blocked", "plana_ac")
            elif not blokajlar:
                ekle("alan", "hata", tid, "blocked ama blokaj listesi boş", "plana_ac")

        # stuck: 24 saatten uzun süredir hareketsiz açık görev (bilgi amaçlı)
        if durum not in KAPALI_DURUMLAR:
            son = _son_hareket(gorev)
            if son and simdi - son > STUCK_ESIK:
                ekle("stuck", "uyari", tid,
                     f"{durum} / son hareket {son.isoformat(timespec='minutes')}")

    # kuyruk senkronu. Kuyruk bir ekleme-günlüğüdür: aynı task_id birden çok kez
    # geçebilir, görev onaydan sonra yeniden açılmış olabilir.
    for kayit in kuyruk:
        tid = kayit.get("task_id")
        if tid not in kimlikler:
            # D-231: arşivde duran iş öksüz değil, kapanmış iştir. Tek istisna
            # "bekliyor": arşivlenmiş görev için bekleyen onay gerçek çelişkidir.
            if tid in arsiv and kayit.get("durum") != "bekliyor":
                continue
            seviye = "hata" if kayit.get("durum") == "bekliyor" else "uyari"
            ekle("orphan", seviye, tid, f"kuyrukta ({kayit.get('durum')}) var, panoda yok")
            continue
        if kayit.get("durum") != "onaylandi" or durumlar.get(tid) in KAPALI_DURUMLAR:
            continue
        # Kuyruk ekleme-günlüğü olduğu için eski bir onay kaydı, görev sonradan
        # yeniden açıldıysa çelişki değildir. Yeniden açılma her zaman zaman
        # damgası bırakmadığından (bkz. DASH-UX-02b) bu bulgu ASLA otomatik
        # uygulanmaz: durum=done kararı kanıt ister (D-66) ve orkestratöre aittir (D-77).
        onay = _an(kayit.get("onay_tarihi"))
        hareket = _son_hareket(gorevler[tid])
        if onay and hareket and hareket > onay:
            continue  # onaydan sonra yeniden açılmış: tarihsel kayıt
        ekle("kuyruk", "uyari", tid,
             f"kuyruk=onaylandi ama pano={durumlar.get(tid)} — orkestratör kanıtla kapatmalı")

    return bulgular


def ithalat_kontrol() -> dict | None:
    """trigger.py'nin göreli ithalatı korunuyor mu (kök neden regresyon bekçisi)."""
    if not TRIGGER_DOSYA.exists():
        return {"tip": "ithalat", "seviye": "hata", "task_id": "trigger.py",
                "mesaj": "dosya yok", "duzeltme": None}
    metin = TRIGGER_DOSYA.read_text(encoding="utf-8")
    if "import task_board as tb" in metin:
        return None
    return {"tip": "ithalat", "seviye": "hata", "task_id": "trigger.py",
            "mesaj": "task_board ithalatı bozulmuş (beklenen: '... import task_board as tb')",
            "duzeltme": None}


def _kanonik_yol_kontrol() -> dict | None:
    """D-186: Pano dosyası kanonik konumda mı? Reel worktree'lerde split var mı?"""
    # YA-03: kanoniklik olcutu dizin ADI degil, depo KOKUNE gorelilik.
    # Depo baska adla klonlanirsa test/denetim kirilmasin; olcut:
    # tb.STATE_DIR bu deponun data/orchestrator dizinini mi gosteriyor?
    kanonik = (ROOT / "data" / "orchestrator" / "task_board.json").resolve()
    if PANO_DOSYA.resolve() != kanonik:
        return {
            "tip": "split",
            "seviye": "hata",
            "task_id": "pano_denetim",
            "mesaj": f"PANO_DOSYA kanonik yolda değil: {PANO_DOSYA} (beklenen: {kanonik})",
            "duzeltme": None
        }
    
    # Reel worktree'lerde split türemesi var mı? (iç içe worktree'ler dahil)
    for split in ROOT.glob(".kilo/worktrees/**/data/orchestrator/task_board.json"):
        return {
            "tip": "split",
            "seviye": "hata",
            "task_id": "pano_denetim",
            "mesaj": f"Reel worktree'de split tespit: {split}",
            "duzeltme": None
        }

    return None


def arsivlenebilir(pano: list[dict], kuyruk: list[dict], simdi: datetime) -> list[str]:
    onayli = {k.get("task_id") for k in kuyruk if k.get("durum") == "onaylandi"}
    sonuc = []
    for gorev in pano:
        if gorev.get("durum") != "done" or gorev.get("task_id") not in onayli:
            continue
        son = _son_hareket(gorev)
        if son and simdi - son > ARSIV_ESIK:
            sonuc.append(gorev["task_id"])
    return sonuc


# Otomat yalnızca geri alınabilir, kanıt gerektirmeyen düzeltmeleri yapar.
# "done" yazmak kanıt doğrulaması ister (D-66) ve orkestratörün yetkisindedir (D-77).
IZINLI_DUZELTMELER = ("plana_ac", "bitis_temizle")


def uygula(bulgular: list[dict], arsiv: list[str]) -> list[str]:
    """Düzeltmeleri yetkili yoldan (task_board API) yazar; yapılanları döner."""
    from src.company_master.orchestrator import task_board as tb

    yapilan = []
    for b in bulgular:
        duzeltme, tid = b.get("duzeltme"), b.get("task_id")
        if duzeltme not in IZINLI_DUZELTMELER:
            continue
        if duzeltme == "plana_ac":
            tb.gorev_guncelle(tid, durum="plan")
        elif duzeltme == "bitis_temizle":
            tb.gorev_guncelle(tid, bitis=None)
        yapilan.append(f"{tid}:{duzeltme}")
    for tid in arsiv:
        tb.gorev_guncelle(tid, durum="archive")
        yapilan.append(f"{tid}:archive")
    return yapilan


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pano tutarlılık denetimi ve senkronizasyonu")
    ap.add_argument("--uygula", action="store_true", help="tespit edilen uyumsuzlukları düzelt")
    args = ap.parse_args(argv)

    simdi = datetime.now()
    rapor: dict = {"timestamp": simdi.isoformat(timespec="seconds"), "status": "ok",
                   "uygula": args.uygula, "bulgular": [], "gorevler": [], "duzeltilen": [],
                   "error": None}
    try:
        # D-186: Split prevention bekçi — pano dosyası kanonik yolda mı?
        split_hata = _kanonik_yol_kontrol()
        if split_hata:
            rapor["bulgular"] = [split_hata]
            rapor["status"] = "fail"
            rapor["hata_sayisi"] = 1
            RAPOR_DOSYA.write_text(json.dumps(rapor, indent=2, ensure_ascii=False), encoding="utf-8")
            return 1

        pano = _json_oku(PANO_DOSYA)
        kuyruk = _json_oku(KUYRUK_DOSYA)
        arsiv_kimlik = arsiv_kimlikleri()  # D-231: bir kez oku, iki taramada kullan

        bulgular = tara(pano, kuyruk, simdi, arsiv_kimlik)
        ithalat = ithalat_kontrol()
        if ithalat:
            bulgular.append(ithalat)
        arsiv = arsivlenebilir(pano, kuyruk, simdi) if args.uygula else []

        if args.uygula:
            # Sessiz basari yasagi: duzeltme adayi varken hicbiri yazilmadiysa
            # komut "yaptim" deyip cikmamali. aday>0 & yapilan=0 -> exit 2.
            aday = [b for b in bulgular if b.get("duzeltme") in IZINLI_DUZELTMELER]
            rapor["aday_sayisi"] = len(aday) + len(arsiv)
            rapor["duzeltilen"] = uygula(bulgular, arsiv)
            pano = _json_oku(PANO_DOSYA)
            kuyruk = _json_oku(KUYRUK_DOSYA)
            bulgular = tara(pano, kuyruk, simdi, arsiv_kimlik) + ([ithalat] if ithalat else [])

        rapor["bulgular"] = bulgular
        rapor["gorevler"] = [
            {"id": g.get("task_id"), "durum": g.get("durum"),
             "update": (lambda s: s.isoformat(timespec="minutes") if s else None)(_son_hareket(g))}
            for g in pano if g.get("durum") not in KAPALI_DURUMLAR
        ]
        hatalar = [b for b in bulgular if b.get("seviye") == "hata"]
        rapor["hata_sayisi"] = len(hatalar)
        rapor["status"] = "ok" if not hatalar else "fail"
        if args.uygula and rapor.get("aday_sayisi") and not rapor["duzeltilen"]:
            rapor["status"] = "noop"
    except Exception as exc:  # rapor her koşulda yazılmalı
        rapor["status"] = "fail"
        rapor["error"] = f"{exc}\n{traceback.format_exc()}"

    RAPOR_DOSYA.parent.mkdir(parents=True, exist_ok=True)
    RAPOR_DOSYA.write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")

    for b in rapor["bulgular"]:
        print(f"  [{b.get('seviye')}/{b['tip']}] {b['task_id']}: {b['mesaj']}")
    if rapor["duzeltilen"]:
        print(f"  DUZELTILEN: {', '.join(rapor['duzeltilen'])}")
    print(f"[PANO-DENETIM] status={rapor['status']} hata={rapor.get('hata_sayisi', 0)} "
          f"uyari={len(rapor['bulgular']) - rapor.get('hata_sayisi', 0)} "
          f"acik_gorev={len(rapor['gorevler'])} rapor={RAPOR_DOSYA.name}")
    if rapor["error"]:
        print(rapor["error"], file=sys.stderr)
    if rapor["status"] == "noop":
        print(f"HATA: --uygula verildi, {rapor['aday_sayisi']} duzeltme adayi vardi, "
              "hicbiri yazilamadi.", file=sys.stderr)
        return 2
    # ponytail: alarm = exit 1 (CI bildirimi). Ayrı e-posta/webhook gerekirse CI adımına ekle.
    return 0 if rapor["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
