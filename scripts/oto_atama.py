"""Orkestratör — P2-5: İç Ajan Otomatik Görev Atama.

TODO.md'deki plan görevlerini okur, her birini en uygun iç ajana atar,
dosya-lock ile çakışma kontrolü yapar ve panoya ekler.

Kullanim:
    python scripts/oto_atama.py --dry-once     (tek sefer, rapor)
    python scripts/oto_atama.py --calistir     (panoya yaz)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.orchestrator import internal, task_board  # noqa: E402

# Görev -> iç ajan eşleşmesi (anahtar kelime eşleşmesi)
GOREV_ESLESME: list[tuple[str, str, str]] = [
    # (regex_pattern, ic_ajan_id, oncelik)
    (r"scraper|scrape|kazıma|robots|rate.?limit|web.?kaz", "web_kazima", "P1"),
    (r"mimari|şema|schema|migration|ETL tasarım|mimari karar", "mimar", "P1"),
    (r"araştır|API|MERSİS|ticaret sicili|KVKK|legal|kaynak", "arastirmaci", "P1"),
    (r"implement|kod|test|coverage|refactor|entegr|ingest|pipeline", "gelistirici", "P1"),
    (r"kalite|KPI|review|doğrulama|test coverage|optimiz", "kalite", "P2"),
    (r"koordin|revize|yol haritası|genel|proje durum", "koordinatör", "P2"),
    (r"dashboard|Streamlit|state|rapor panel", "gelistirici", "P2"),
    (r"multi.?OSB|merger|birleştir", "gelistirici", "P1"),
    (r"NACE|sektor|eşleştirme", "gelistirici", "P1"),
    (r"Telegram|bot|polling|servis", "gelistirici", "P1"),
]


def _eslesen_ajan(baslik: str) -> tuple[str, str]:
    """Başlık metnine göre (ajan_id, oncelik) döndürür."""
    metin = baslik.lower()
    for pattern, ajid, oncelik in GOREV_ESLESME:
        if re.search(pattern, metin, re.IGNORECASE):
            return ajid, oncelik
    return "gelistirici", "P2"  # default


def _mevcut_gorev_idleri() -> set[str]:
    return {t["task_id"] for t in task_board.gorev_listesi()}


def todo_dan_plan_gorevleri() -> list[dict]:
    """TODO.md'deki plan durumundaki görevleri çıkarır."""
    todo = ROOT / "AI proje v1" / "V10" / "TODO.md"
    if not todo.exists():
        return []
    metin = todo.read_text(encoding="utf-8")
    gorevler: list[dict] = []
    # Tablo satırlarını bul: | ID | Görev | Sahip | Durum | Not |
    for satir in metin.splitlines():
        satir = satir.strip()
        if not satir.startswith("|"):
            continue
        parcalar = [p.strip() for p in satir.split("|")]
        if len(parcalar) < 5:
            continue
        task_id = parcalar[1]
        baslik = parcalar[2]
        sahip = parcalar[3]
        durum = parcalar[4]
        # Başlık satırlarını ve ayraçları atla
        if not task_id or not baslik or task_id.startswith("--"):
            continue
        if durum.lower() not in ("plan", "aktif", "blocked"):
            continue
        if task_id in ("ID",):
            continue
        gorevler.append({
            "task_id": task_id,
            "baslik": baslik,
            "sahip_todo": sahip,
            "durum": durum,
        })
    return gorevler


def calistir(dry: bool = False) -> int:
    mevcut = _mevcut_gorev_idleri()
    planli = todo_dan_plan_gorevleri()
    atanan = 0
    atlanan = 0

    print(f"TODO'dan {len(planli)} plan görev bulundu, panoda {len(mevcut)} görev var\n")

    for g in planli:
        tid = g["task_id"]
        if tid in mevcut:
            print(f"  [ATLA] {tid} — zaten panoda")
            atlanan += 1
            continue

        # Otomatik eşleşme
        ajid, oncelik = _eslesen_ajan(g["baslik"])
        # TODO'da sahip yazıyorsa onu tercih et (eşleşme ile çakışmazsa)
        sahip = g["sahip_todo"] if g["sahip_todo"] in internal.ic_ajanlar() else ajid

        if dry:
            print(f"  [DRY ] {tid:<8} -> {sahip:<14} [{oncelik}] {g['baslik'][:50]}")
            atanan += 1
            continue

        try:
            task_board.gorev_ekle(
                task_id=tid,
                baslik=g["baslik"],
                sahip=sahip,
                oncelik=oncelik,
            )
            print(f"  [OK  ] {tid:<8} -> {sahip:<14} [{oncelik}] {g['baslik'][:50]}")
            atanan += 1
        except (ValueError, PermissionError) as exc:
            print(f"  [HATA] {tid}: {exc}")
            atlanan += 1

    print(f"\nToplam: {atanan} atandı, {atlanan} atlandı")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="oto-atama")
    parser.add_argument("--dry-once", action="store_true", help="Sadece rapor, panoya yazma")
    parser.add_argument("--calistir", action="store_true", help="Panoya yaz")
    args = parser.parse_args()
    return calistir(dry=not args.calistir)


if __name__ == "__main__":
    sys.exit(main())