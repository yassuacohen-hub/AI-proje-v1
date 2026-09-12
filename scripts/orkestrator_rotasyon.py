# -*- coding: utf-8 -*-
"""Orkestratör rotasyonu — sahip ritüeli "abrakadabra" ile tek komutluk devir teslim.

Amaç: kimin orkestratör olduğu tek kaynaktan (decision_log.jsonl) okunur;
rotasyon yalnızca sahibin sözüyle başlar ve yapılandırılmış kayıtla kanıtlanır.

Kayıt şeması (JSONL, action=orkestrator_rotasyonu):
    {"action": "orkestrator_rotasyonu", "kimden": "cline", "kime": "roo",
     "tetikleyici": "sahip", "ts": "...", "gerekce": "..."}

Kullanım:
    python scripts/orkestrator_rotasyon.py --kim
        # aktif orkestratörü söyler (son rotasyon kaydı; kayıt yoksa varsayılan)

    python scripts/orkestrator_rotasyon.py roo --kelime abrakadabra --gerekce "..."
        # rotasyon: kaydı JSONL'e atar + Obsidian CHANGELOG'a not düşer

Kurallar (AGENTS.md "Orkestratör Rotasyonu" bölümü):
    - Rotasyon cümlesi görev cümlesiyle aynı mesajda birleştirilmez.
    - Yanlış ritüel sözcüğünde kayıt atılmaz (PermissionError).
    - Aynı orkestratöre "kendine" rotasyon da kayda değer (baseline tespiti).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "data" / "orchestrator" / "decision_log.jsonl"
CHANGELOG = ROOT / "AI proje v1" / "V10" / "CHANGELOG.md"

RITUEL = "abrakadabra"           # sahip ritüel sözcüğü
BASLANGIC_ORKESTRATOR = "cline"  # hiç rotasyon kaydı yokken varsayılan


def _kayitlari_oku(log_path: Path) -> list[dict[str, Any]]:
    """JSONL dosyasını satır satır okur; bozuk satırları atlar."""
    if not log_path.exists():
        return []
    kayitlar: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            kayitlar.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return kayitlar


def _rotasyon_kaydi_mi(kayit: dict[str, Any]) -> bool:
    """Karışık şemalı log içinden rotasyon kayıtlarını ayırt eder."""
    if kayit.get("action") == "orkestrator_rotasyonu":
        return True
    return "orkestrator rotasyonu" in str(kayit.get("title", "")).lower()


def aktif_orkestrator(log_path: Path = LOG) -> str:
    """Son rotasyon kaydındaki 'kime' değerini döner; kayıt yoksa varsayılanı."""
    sonuc = BASLANGIC_ORKESTRATOR
    for kayit in _kayitlari_oku(log_path):
        if _rotasyon_kaydi_mi(kayit):
            kime = str(kayit.get("kime", "")).strip()
            if kime:
                sonuc = kime
    return sonuc


def _kayit_ekle(kayit: dict[str, Any], log_path: Path) -> None:
    """Rotasyon kaydını JSONL sonuna ekler (tek satır, append-only)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(kayit, ensure_ascii=False) + "\n")


def _changelog_yaz(kimden: str, kime: str, gerekce: str, changelog_path: Path) -> bool:
    """Obsidian CHANGELOG'a insan-okur rotasyon notu düşer (ilk tarihli başlıktan önce)."""
    if not changelog_path.exists():
        return False
    tarih = datetime.now().strftime("%Y-%m-%d")
    satirlar = [
        f"## [{tarih}] Orkestratör Rotasyonu: {kimden} → {kime}",
        "",
        "- Sahip ritüeli `abrakadabra` ile tetiklendi; kayıt: `data/orchestrator/decision_log.jsonl` (action: `orkestrator_rotasyonu`)",
        "- Aktif orkestratör sorgulama: `python scripts/orkestrator_rotasyon.py --kim`",
    ]
    if gerekce:
        satirlar.append(f"- Gerekçe: {gerekce}")
    satirlar.append("")
    text = changelog_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    idx = next((i for i, ln in enumerate(lines) if ln.startswith("## [")), None)
    if idx is None:
        return False
    lines[idx:idx] = satirlar
    changelog_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return True


def rotasyon_yap(
    kime: str,
    kelime: str,
    gerekce: str = "",
    log_path: Path = LOG,
    changelog_path: Path = CHANGELOG,
) -> dict[str, Any]:
    """Rotasyon kaydı atar; yanlış ritüel sözcüğünde reddeder.

    Returns:
        Atılan yapılandırılmış rotasyon kaydı.

    Raises:
        ValueError: yeni orkestratör adı boşsa.
        PermissionError: ritüel sözcüğü hatalıysa (kayıt atılmaz).
    """
    kime = (kime or "").strip().lower()
    if not kime:
        raise ValueError("Yeni orkestratör adı boş olamaz.")
    if kelime != RITUEL:
        raise PermissionError("Ritüel sözcüğü hatalı — rotasyon kaydı atılmadı.")
    kimden = aktif_orkestrator(log_path)
    kayit: dict[str, Any] = {
        "action": "orkestrator_rotasyonu",
        "kimden": kimden,
        "kime": kime,
        "tetikleyici": "sahip",
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "gerekce": gerekce,
    }
    _kayit_ekle(kayit, log_path)
    _changelog_yaz(kimden, kime, gerekce, changelog_path)
    return kayit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("kime", nargs="?", help="yeni orkestratör adı (örn. roo, kilo, cline)")
    parser.add_argument("--kelime", help="sahip ritüel sözcüğü")
    parser.add_argument("--gerekce", default="", help="rotasyon gerekçesi (kayda düşer)")
    parser.add_argument("--kim", action="store_true", help="aktif orkestratörü söyler ve çıkar")
    args = parser.parse_args(argv)

    if args.kim:
        print(aktif_orkestrator())
        return 0
    if not args.kime:
        parser.error("ya --kim kullan ya da yeni orkestratör adı ver")
    try:
        kayit = rotasyon_yap(args.kime, args.kelime or "", args.gerekce)
    except (ValueError, PermissionError) as e:
        print(f"REDDEDİLDİ: {e}", file=sys.stderr)
        return 2
    print(f"ROTASYON KAYDI ATILDI: {kayit['kimden']} → {kayit['kime']} ({kayit['ts']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
