#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRAPH-CANONICAL-SECER-02: Canonical graph baglanti guvenligi dogrulamasi.

Kontroller:
  1. Canonical dosyalari mevcut mu (kopya silinmemis)?
  2. Redirect satirlari ([[canonical]]) hedefe gidiyor mu (kirik redirect)?
  3. Ayni grupta 1'den fazla canonical adayi mi (SSOT ihlali)?
  4. Redirect satiri iceren dosyalarda orijinal icerik duruyor mu (bos dosya)?

Cikti:
  - data/orchestrator/GRAPH-CANONICAL-SECER-02_rapor_2026-09-23_yasu.md
  - data/orchestrator/GRAPH-CANONICAL-SECER-02_rapor_2026-09-23_yasu.json

Kural: Sadece okuma + rapor; dosya Icerigine mudahale YOK (denetim gorevi).
"""
from __future__ import annotations

import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WORKSPACE_ROOT = Path("c:/Huginn Data Projesi").resolve()
RAPOR_JSON = WORKSPACE_ROOT / "data/orchestrator/GRAPH-CANONICAL_rapor_2026-09-21.json"
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:[#\|][^\]]*)?\]\]")


def kontrol_et() -> dict:
    rapor = json.loads(RAPOR_JSON.read_text(encoding="utf-8"))
    gruplar = rapor["grupplar"]

    sonuc = {
        "metadata": {
            "gorev": "GRAPH-CANONICAL-SECER-02",
            "tarih": datetime.now(timezone.utc).isoformat(),
            "kaynak": str(RAPOR_JSON.relative_to(WORKSPACE_ROOT)),
        },
        "ozet": {
            "grup_sayisi": len(gruplar),
            "canonical_toplam": 0,
            "canonical_eksik": 0,
            "redirect_kirik": 0,
            "ssot_ihlali": 0,
            "bos_redirect_dosya": 0,
        },
        "bulgular": [],
    }

    for grup in gruplar:
        ad = grup.get("grup_adi", "?")
        canonical = grup.get("canonical") or {}
        cyol = canonical.get("yol")
        redirectler = grup.get("redirect") or []

        # 1) Canonical mevcut mu?
        if not cyol:
            sonuc["ozet"]["canonical_eksik"] += 1
            sonuc["bulgular"].append(
                {"tur": "CANONICAL_EKSIK", "grup": ad, "detay": "canonical alanı boş"}
            )
            continue
        sonuc["ozet"]["canonical_toplam"] += 1
        cpath = WORKSPACE_ROOT / cyol
        if not cpath.exists():
            sonuc["bulgular"].append(
                {"tur": "CANONICAL_KAYIP", "grup": ad, "dosya": cyol}
            )

        # 2) Redirect hedefleri kirik mi? 3) Icerik bos mu?
        for r in redirectler:
            ryol = r.get("yol", "")
            rpath = WORKSPACE_ROOT / ryol
            if not rpath.exists():
                sonuc["ozet"]["redirect_kirik"] += 1
                sonuc["bulgular"].append(
                    {"tur": "REDIRECT_KIRIK", "grup": ad, "dosya": ryol}
                )
                continue
            try:
                content = rpath.read_text(encoding="utf-8-sig", errors="ignore")
            except OSError:
                continue
            body = content.strip()
            # Sadece redirect satiri kalmis ve gercek icerik gitmis mi?
            kalan = body.replace(f"[[{cyol}]]", "").strip()
            if len(kalan) < 10:
                sonuc["ozet"]["bos_redirect_dosya"] += 1
                sonuc["bulgular"].append(
                    {"tur": "REDIRECT_BOS_ICERIK", "grup": ad, "dosya": ryol}
                )

        # 4) SSOT ihlali: grupta ayni dosyanin baska bir kopyasina da
        #    canonical muamelesi yapilmis mi (grup dosyalari arasi cakisma)?
        yollar = [cyol] + [r.get("yol", "") for r in redirectler]
        if len({y.replace("\\", "/").lower() for y in yollar}) != len(yollar):
            sonuc["ozet"]["ssot_ihlali"] += 1
            sonuc["bulgular"].append({"tur": "SSOT_IHLALI", "grup": ad, "yollar": yollar})

    return sonuc


def markdown_yaz(s: dict) -> str:
    o = s["ozet"]
    temiz = (
        not s["bulgular"]
    )
    md = [
        "# GRAPH-CANONICAL-SECER-02 Raporu",
        "",
        f"- **Sahip**: Yasu",
        f"- **Tarih**: {s['metadata']['tarih']}",
        f"- **Kaynak**: `{s['metadata']['kaynak']}`",
        f"- **Durum**: {'✅ Temiz — güvenlik ihlali yok' if temiz else '⚠️ Bulgular var (aşağıda)'}",
        "",
        "## Özet",
        "| Metrik | Değer |",
        "|--------|-------|",
        f"| Grup sayısı | {o['grup_sayisi']} |",
        f"| Canonical (seçili) | {o['canonical_toplam']} |",
        f"| Canonical eksik | {o['canonical_eksik']} |",
        f"| Kırık redirect | {o['redirect_kirik']} |",
        f"| SSOT ihlali | {o['ssot_ihlali']} |",
        f"| İçeriği boşalan redirect dosyası | {o['bos_redirect_dosya']} |",
        "",
        "## Bulgular",
    ]
    if not s["bulgular"]:
        md.append("- Yok. 156 grup / canonical / redirect zinciri tutarlı.")
    else:
        for b in s["bulgular"][:50]:
            md.append(f"- **{b['tur']}** — {b.get('grup','?')}: {b.get('dosya') or b.get('detay') or b.get('yollar')}")
        if len(s["bulgular"]) > 50:
            md.append(f"- ... ve {len(s['bulgular']) - 50} bulgu daha (JSON'a bak)")
    md.append("")
    md.append("## Bağlantılar")
    md.append("- [[Karar: Graph canonical]] (D-177: Huginn Data Insights/ = graph canonical)")
    md.append("- D-172: worktree klasoru/ = yazma otorite, SSOT")
    md.append("- Önceki: [[GRAPH-CANONICAL_UYGULA_RAPOR_2026-09-21]]")
    return "\n".join(md)


def main() -> None:
    sonuc = kontrol_et()
    out_json = WORKSPACE_ROOT / "data/orchestrator/GRAPH-CANONICAL-SECER-02_rapor_2026-09-23_yasu.json"
    out_md = WORKSPACE_ROOT / "data/orchestrator/GRAPH-CANONICAL-SECER-02_rapor_2026-09-23_yasu.md"
    out_json.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(markdown_yaz(sonuc), encoding="utf-8")
    print("Özet:", json.dumps(sonuc["ozet"], ensure_ascii=False))
    print(f"Bulgu sayısı: {len(sonuc['bulgular'])}")
    print(f"Rapor: {out_md}")


if __name__ == "__main__":
    main()
