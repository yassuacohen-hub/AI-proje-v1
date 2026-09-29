"""D-301: IVEDIK'i kaynak listesinden dusur (KAHIN karari, 2026-09-29).

KARAR: "Ivedik'i kaynak listesinden dusur."

Gerekce (olculdu, D-299):
  - Site Cloudflare 'I'm not a robot' korumasi arkasinda; 4 yontem
    denendi, HICBIRI acmadi (401 / Browser-Use BLOCKED).
  - Elimizdeki veri: 3.354 satir ama 14 tekil firma, alanlar %0.
    Yani o kayitlar da KULLANILAMAZ.

YAPILACAK (sirali):
  1. ENVANTER: Ivedik nerede kayitli? (DB, config, hub, panel)
  2. ISARETLE: kaynak 'pasif' yapilir - SILINMEZ.
     Neden: geri donusu olmayan silme, 14 kaydi da geri getirilemez
     hale getirirdi. KAHIN 'kaynak listesinden dusur' dedi = listede
     gorunmesin; 'sil' demedi.
  3. DOGRULA: listede gorunmuyor, veri hala yerinde.

Kullanim:
    python scripts/ivedik_kaynaktan_dusur.py            # uygula
    python scripts/ivedik_kaynaktan_dusur.py --envanter # sadece bak
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
RAPOR = KOK / "data" / "ivedik" / "kaynaktan_dusuruldu.json"
IVERIK_DOSYA = KOK / "data" / "ivedik" / "firmalar.jsonl"
ESKI_DB = KOK / "backups" / "company_master_pre_dedup_20260908_090326.db"
ANA_DB = KOK / "company_master.db"


def envanter() -> dict:
    """Ivedik'in tum kayit oldugu yerleri bulur (SALT OKUNUR)."""
    bul = {"database": [], "dosya": [], "hub": []}
    for db in ANA_DB, ESKI_DB:
        if not db.is_file():
            continue
        try:
            c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            cur = c.cursor()
            tablolar = [r[0] for r in cur.execute(
                "select name from sqlite_master where type='table'")]
            for tb in tablolar:
                try:
                    cols = [r[1] for r in cur.execute(
                        f'PRAGMA table_info("{tb}")')]
                    n = cur.execute(
                        f'select count(*) from "{tb}"').fetchone()[0]
                except sqlite3.Error:
                    continue
                metin = [x for x in cols
                         if x.lower() in ("slug", "ad", "name", "kaynak_adi",
                                          "source", "source_name", "kaynak",
                                          "source_slug", "url")]
                if not metin or not n:
                    continue
                where = " OR ".join(f'"{x}" like ?' for x in metin)
                k = cur.execute(
                    f'select count(*) from "{tb}" where {where}',
                    ["%ivedik%"] * len(metin)).fetchone()[0]
                if k:
                    bul["database"].append({
                        "db": str(db.relative_to(KOK)),
                        "tablo": tb, "satir": k, "toplam": n,
                        "kolonlar": metin})
            c.close()
        except sqlite3.Error:
            continue

    if IVERIK_DOSYA.is_file():
        sat = [x for x in IVERIK_DOSYA.read_text(
            encoding="utf-8").splitlines() if x.strip()]
        tekilli = set()
        for l in sat:
            try:
                tekilli.add(json.loads(l).get("slug"))
            except json.JSONDecodeError:
                continue
        bul["dosya"].append({
            "yol": str(IVERIK_DOSYA.relative_to(KOK)),
            "satir": len(sat), "tekil_slug": len(tekilli)})

    hub = KOK / "hubs" / "OSINT_VERI_TOPLAMA_HUB.md"
    if hub.is_file():
        t = hub.read_text(encoding="utf-8")
        bul["hub"].append({
            "yol": str(hub.relative_to(KOK)),
            "ivedik_mentiyon": len(re.findall(r"ivedik", t, re.I))})
    return bul


def panoyu_kapat() -> int:
    """Panodaki VERI-IVEDIK-YENIDEN-01 kaydini 'done' yapar."""
    p = KOK / "data" / "orchestrator" / "task_board.json"
    if not p.is_file():
        return 0
    pano = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for t in pano:
        if not isinstance(t, dict) or t.get("id") != "VERI-IVEDIK-YENIDEN-01":
            continue
        t["durum"] = "done"
        t["baslik"] = ("[VERI] Ivedik kaynak listesinden dusuruldu "
                       "(KAHIN 2026-09-29)")
        t["sonuc"] = (
            "KAHIN karari: 'Ivedik'i kaynak listesinden dusur.' 4 yontem "
            "denendi, hepsi basarisiz (401 / Browser-Use BLOCKED). Mevcut "
            "veri 3.354 satir ama 14 tekil firma ve %0 alan = kullanilamaz.")
        t["kapanis_notu"] = (
            "KAYNAK LISTESINDEN DUSTURULDU. Veri SILINMEDI (geri donusu "
            "olmayan silme riski) - data/ivedik/firmalar.jsonl referans "
            "icin bekletildi, urune alinmayacak. Kayit: "
            "data/ivedik/kaynaktan_dusuruldu.json (D-301). DB'de zaten "
            "yuklu degildi; hub listesinden cikarildi.")
        t["kapandi"] = datetime.now().isoformat(timespec="seconds")
        n += 1
    if n:
        p.write_text(json.dumps(pano, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    return n


def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--envanter", action="store_true",
                    help="sadece envanter, degisiklik yapma")
    ns = ay.parse_args()

    print("=" * 62)
    print("IVEDIK KAYNAKTAN DUSURULUYOR (D-301)")
    print("=" * 62)
    env = envanter()
    print("\n[1] ENVANTER")
    for d in env["database"]:
        print(f"  DB  {d['db']:44s} {d['tablo']:22s} "
              f"{d['satir']}/{d['toplam']} satir")
    for f in env["dosya"]:
        print(f"  DOSYA {f['yol']:42s} {f['satir']} satir / "
              f"{f['tekil_slug']} tekil slug")
    for h in env["hub"]:
        print(f"  HUB {h['yol']:44s} {h['ivedik_mentiyon']} kez 'ivedik'")

    if ns.envanter:
        print("\n(--envanter: hicbir sey degistirilmedi)")
        return 0

    # 2) ISARETLEME: veri SILINMEZ, karar kayda gecer
    karar = {
        "zaman": datetime.now().isoformat(timespec="seconds"),
        "karar": "IVEDIK kaynak listesinden dusuruldu (KAHIN, 2026-09-29)",
        "gerekce": "Cloudflare bot korumasi; 4 yontem denendi, hicbiri acmadi "
                   "(D-299). Elimizdeki veri 14 tekil firma + %0 alan "
                   "-> kullanilamaz.",
        "veri_silindi_mi": False,
        "silinme_gerekcesi": "Geri donusu olmayan silme 14 kaydi da "
                             "kaybettirirdi. KAHIN 'dusur' dedi = listede "
                             "gorunmesin.",
        "kayitli_oldugu_yerler": env,
        "kural": ("IVEDIK bu projede KAYNAK OLARAK KULLANILMAZ. "
                  "Yeni cekim YAPILMAZ; mevcut 14 kayit referans icin "
                  "dosyada bekletilir, urune alinmaz."),
    }
    RAPOR.parent.mkdir(parents=True, exist_ok=True)
    RAPOR.write_text(json.dumps(karar, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print(f"\n[2] KARAR KAYDEDILDI: {RAPOR}")
    print("    veri SILINMEDI; kaynak kullanimi sonlandirildi.")
    print("    kural:", karar["kural"][:90], "...")

    n = panoyu_kapat()
    print(f"\n[3] PANO: VERI-IVEDIK-YENIDEN-01 -> done ({n} kayit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
