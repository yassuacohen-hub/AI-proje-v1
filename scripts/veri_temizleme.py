#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""YENI-1 — Veri Temizleme Scripti.

Amac
----
Ham JSONL verilerindeki ortak kalite sorunlarini düzeltmek:
  - Encoding (mojibake) düzeltmesi
  - Portal kaynakli sahte zenginlik filtreleme (web_sitesi, sosyal medya)
  - VKN, telefon, e-posta format dogrulama ve normalize
  - URL normalize (protocol, trailing slash)
  - Bos/null alan temizleme
  - Duplicate kayit tespiti ve cikarma
  - Unvan temizleme (trim, bosluk, tabela kisaaltmalari)

Kullanim
--------
    python scripts/veri_temizleme.py                        # OSTIM + ASO
    python scripts/veri_temizleme.py --source ostim          # Sadece OSTIM
    python scripts/veri_temizleme.py --source aso            # Sadece ASO
    python scripts/veri_temizleme.py --input data/ostim/firmalar_detayli.jsonl --output data/ostim/clean.jsonl
    python scripts/veri_temizleme.py --report               # Rapor olustur (varsayilan: cikti yaninda)

Cikis
-----
    <input>_clean.jsonl     Temizlenmis kayitlar
    <input>_report.json     Temizleme raporu (istatistik + sorunlar)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

COMPANY_TYPE_ABBR = {
    "ANONIM SIRKETI": "A.S.", "ANONIM SIRKET": "A.S.", "ANONIM ORTAKLIK": "A.S.",
    "LIMITED SIRKETI": "LTD. STI.", "LIMITED SIRKET": "LTD. STI.",
    "KOLLEKTIF SIRKETI": "KOL. STI.", "KOMANDIT SIRKETI": "KOM. STI.",
    "ORTAKLIK": "ORT.", "KOOPERATIF": "KOOP.",
    "TURK ANONIM SIRKETI": "T.A.S.", "TURK ANONIM ORTAKLIK": "T.A.S.",
}

PORTAL_DOMAINS = {
    "ostimistihdam.com",
    "www.ostimistihdam.com",
    "ostim.gov.tr",
    "www.ostim.gov.tr",
    "ostim.org.tr",
    "www.ostim.org.tr",
    "asogrubu.com",
    "www.asogrubu.com",
}

PORTAL_SOCIAL_KEYWORDS = {
    "ostim",
    "asogrubu",
    "ankara sanayi odasi",
    "ostim osb",
}

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
URL_RE = re.compile(r"^https?://[a-zA-Z0-9.\-]+")
PHONE_RE = re.compile(r"^(\+?90|0)?[0-9]{10,11}$")
VKN_RE = re.compile(r"^\d{10,11}$")

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
# Yardımcı fonksiyonlar
# ---------------------------------------------------------------------------


def fix_encoding(text: str | None) -> str | None:
    """Mojibake (yazilim karakter uyumsuzluğu) düzeltir.

    UTF-8'de decode edilmemis ISO-8859-9 / CP1254 karakterler
    U+FFFD () olarak gelir. Tekrar encode edip CP1254 olarak
    decode edipTurce karakterleri gerigetirir.
    """
    if not text or "" not in text:
        return text
    try:
        # Stringi Latin-1 olarak geri encode etip CP1254 olarak decode
        return text.encode("latin-1", errors="replace").decode("cp1254", errors="replace")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def normalize_vkn(vkn: Any) -> str | None:
    """VKN formatını normalize eder: 10 veya 11 haneli sayı."""
    if not vkn:
        return None
    vkn_str = str(vkn).strip()
    # Boşlukları ve tireleri kaldır
    vkn_str = re.sub(r"[\s\-\.]", "", vkn_str)
    if VKN_RE.match(vkn_str):
        return vkn_str
    return None


def normalize_phone(phone: Any) -> str | None:
    """Telefon numarasını normalize eder."""
    if not phone:
        return None
    phone_str = str(phone).strip()
    # Varsayılan 0 ön eki varsa +90 yap
    if phone_str.startswith("0") and len(phone_str) == 11:
        phone_str = "+90" + phone_str[1:]
    elif phone_str.startswith("90") and len(phone_str) == 11:
        phone_str = "+" + phone_str
    if PHONE_RE.match(phone_str):
        return phone_str
    return None


def normalize_email(email: Any) -> str | None:
    """E-posta adresini normalize eder."""
    if not email:
        return None
    email_str = str(email).strip().lower()
    if EMAIL_RE.match(email_str):
        return email_str
    return None


def normalize_url(url: Any) -> str | None:
    """URL formatını normalize eder."""
    if not url:
        return None
    url_str = str(url).strip()
    if not URL_RE.match(url_str):
        url_str = "https://" + url_str
    # trailing slash kaldır
    url_str = url_str.rstrip("/")
    # Protocol lowercase
    url_str = re.sub(r"^(https?)://", r"\1://", url_str)
    if URL_RE.match(url_str):
        return url_str
    return None


def is_portal_url(url: str | None) -> bool:
    """URL portal (OSTIM/ASO) kaynağı mı?"""
    if not url:
        return False
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower().replace("www.", "")
        return domain in PORTAL_DOMAINS
    except Exception:
        return False


def is_portal_social(value: Any) -> bool:
    """Sosyal medya URL si portal kaynağı mı?"""
    if not value:
        return False
    value_str = str(value).lower()
    for keyword in PORTAL_SOCIAL_KEYWORDS:
        if keyword in value_str:
            return True
    return False


def clean_unvan(unvan: str | None) -> str | None:
    """Unvanı temizler: trim, fazladan boşlukları birleştirir."""
    if not unvan:
        return None
    unvan = fix_encoding(unvan)
    unvan = unvan.strip()
    # Tabela kısıltma
    for full, abbr in COMPANY_TYPE_ABBR.items():
        if full in unvan:
            unvan = unvan.replace(full, abbr)
    # Tek/triple boşlukları birleştir
    unvan = re.sub(r" {2,}", " ", unvan)
    return unvan if unvan else None


# ---------------------------------------------------------------------------
# Temizleme fonksiyonları
# ---------------------------------------------------------------------------


def clean_ostim_record(record: dict[str, Any]) -> dict[str, Any]:
    """OSTIM kaydını temizler."""
    cleaned: dict[str, Any] = {}
    issues: list[str] = []

    for key, value in record.items():
        # Encoding düzeltme (tüm string alanlar)
        if isinstance(value, str):
            value = fix_encoding(value)

        if key == "unvan":
            value = clean_unvan(value)
        elif key == "vergi_no":
            value = normalize_vkn(value)
        elif key == "telefonlar":
            if isinstance(value, list):
                normalized = []
                for p in value:
                    np = normalize_phone(p)
                    if np:
                        normalized.append(np)
                    else:
                        issues.append(f"telefon_gecersiz: {p}")
                value = normalized if normalized else None
        elif key == "emailler":
            if isinstance(value, list):
                normalized = []
                for e in value:
                    ne = normalize_email(e)
                    if ne:
                        normalized.append(ne)
                    else:
                        issues.append(f"eposta_gecersiz: {e}")
                value = normalized if normalized else None
        elif key in ("web_sitesi",):
            if is_portal_url(value):
                issues.append(f"portal_web: {value}")
                value = None
            else:
                value = normalize_url(value)
        elif key == "sosyal_medya":
            if isinstance(value, dict):
                cleaned_social: dict[str, Any] = {}
                for platform, url in value.items():
                    if is_portal_social(url):
                        issues.append(f"portal_social: {platform}")
                        continue
                    cleaned_social[platform] = normalize_url(url)
                value = cleaned_social if cleaned_social else None
        elif key in ("adres",):
            value = fix_encoding(value)
            if value:
                value = value.strip()
                value = re.sub(r" {2,}", " ", value)
        elif key in ("sektor", "slug", "kaynak"):
            if isinstance(value, str):
                value = value.strip()

        # Null string -> None
        if isinstance(value, str) and value == "":
            value = None

        cleaned[key] = value

    return cleaned, issues


def clean_aso_record(record: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """ASO kaydını temizler."""
    cleaned: dict[str, Any] = {}
    issues: list[str] = []

    for key, value in record.items():
        if isinstance(value, str):
            value = fix_encoding(value)

        if key == "unvan":
            value = clean_unvan(value)
        elif key in ("ticaretSicilNo",):
            if value:
                value = str(value).strip()
        elif key == "naceKod":
            if value:
                value = str(value).strip()
        elif key == "naceDetay":
            if value:
                value = fix_encoding(str(value)).strip()
        elif key == "adres":
            value = fix_encoding(value)
            if value:
                value = value.strip()
                value = re.sub(r" {2,}", " ", value)
        elif key == "eposta":
            ne = normalize_email(value)
            if ne:
                value = ne
            else:
                if value:
                    issues.append(f"eposta_gecersiz: {value}")
                value = None
        elif key == "telefonlar":
            if isinstance(value, list):
                normalized = []
                for p in value:
                    np = normalize_phone(p)
                    if np:
                        normalized.append(np)
                    else:
                        issues.append(f"telefon_gecersiz: {p}")
                value = normalized if normalized else None
        elif key == "yetkililer":
            if isinstance(value, list):
                cleaned_yetkili: list[dict[str, Any]] = []
                for y in value:
                    if isinstance(y, dict):
                        cy: dict[str, Any] = {}
                        for k, v in y.items():
                            if isinstance(v, str):
                                v = fix_encoding(v)
                            cy[k] = v
                        cleaned_yetkili.append(cy)
                value = cleaned_yetkili if cleaned_yetkili else None

        if isinstance(value, str) and value == "":
            value = None

        cleaned[key] = value

    return cleaned, issues


# ---------------------------------------------------------------------------
# Ana işlev
# ---------------------------------------------------------------------------


def process_file(
    input_path: Path,
    output_path: Path,
    report_path: Path,
    source_type: str,
) -> dict[str, Any]:
    """Bir dosyayı işler ve rapor döndürür."""
    stats: dict[str, Any] = {
        "input_file": str(input_path),
        "output_file": str(output_path),
        "source_type": source_type,
        "toplam_kayit": 0,
        "temizlenen": 0,
        "atilan": 0,
        "duzenlenen": 0,
        "sorunlar": defaultdict(int),
        "ortala_duzenlenen": 0,
        "zaman": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sample_sorunlar": [],
    }

    cleaned_records: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    duplicate_count = 0

    if not input_path.exists():
        stats["hata"] = f"Dosya yok: {input_path}"
        return stats

    with open(input_path, encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            stats["toplam_kayit"] += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                stats["atilan"] += 1
                stats["sorunlar"][f"json_hata"] += 1
                if len(stats["sample_sorunlar"]) < 10:
                    stats["sample_sorunlar"].append(f"line {line_num}: {e}")
                continue

            if source_type == "ostim":
                cleaned, issues = clean_ostim_record(record)
            else:
                cleaned, issues = clean_aso_record(record)

            # Duplicate kontrolü
            record_key = json.dumps(cleaned, ensure_ascii=False, sort_keys=True)
            if record_key in seen_keys:
                duplicate_count += 1
                stats["sorunlar"]["duplicate"] += 1
                if len(stats["sample_sorunlar"]) < 10:
                    stats["sample_sorunlar"].append(
                        f"line {line_num}: duplicate (unvan={cleaned.get('unvan', '')[:50]})"
                    )
                continue
            seen_keys.add(record_key)

            # Sorun kaydı
            for issue in issues:
                issue_key = issue.split(":")[0].strip()
                stats["sorunlar"][issue_key] += 1
                if len(stats["sample_sorunlar"]) < 20:
                    stats["sample_sorunlar"].append(f"line {line_num}: {issue}")

            # İstatistik
            if issues:
                stats["duzenlenen"] += 1
            else:
                stats["ortala_duzenlenen"] += 1
            stats["temizlenen"] += 1

            cleaned_records.append(cleaned)

    # Çıktı yaz
    with open(output_path, "w", encoding="utf-8") as f:
        for rec in cleaned_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    stats["cikti_kayit"] = len(cleaned_records)
    stats["duplicate_cikarilan"] = duplicate_count
    stats["sorunlar"] = dict(stats["sorunlar"])

    # Rapor yaz
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Veri Temizleme Scripti — JSONL verilerinden ortak kalite sorunlarını düzeltir.",
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Girdi JSONL dosyası",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Çıktı JSONL dosyası",
    )
    parser.add_argument(
        "--report", "-r",
        type=str,
        default=None,
        help="Rapor JSON dosyası",
    )
    parser.add_argument(
        "--source", "-s",
        choices=["ostim", "aso", "auto"],
        default="auto",
        help="Kaynak tipi",
    )

    args = parser.parse_args()

    if args.input:
        input_path = Path(args.input)
        output_path = Path(args.output) if args.output else input_path.parent / f"{input_path.stem}_clean{input_path.suffix}"
        report_path = Path(args.report) if args.report else input_path.parent / f"{input_path.stem}_report.json"

        if args.source == "auto":
            source_type = "ostim" if "ostim" in str(input_path).lower() else "aso"
        else:
            source_type = args.source

        stats = process_file(input_path, output_path, report_path, source_type)

        print(f"Girdi: {input_path}")
        print(f"Çıktı: {output_path}")
        print(f"Rapor: {report_path}")
        print(f"Toplam: {stats['toplam_kayit']}")
        print(f"Temizlenen: {stats['temizlenen']}")
        print(f"Duzenlenen: {stats['duzenlenen']}")
        print(f"Ortalama düzgün: {stats['ortala_duzenlenen']}")
        print(f"Atılan: {stats['atilan']}")
        print(f"Duplicate: {stats.get('duplicate_cikarilan', 0)}")
        if stats.get("hata"):
            print(f"HATA: {stats['hata']}")
        if stats.get("sorunlar"):
            print("Sorunlar:")
            for k, v in stats["sorunlar"].items():
                print(f"  {k}: {v}")
        return 0

    # Varsayılan: OSTIM + ASO işle
    inputs = [
        (ROOT / "data" / "ostim" / "firmalar_detayli.jsonl", "ostim"),
        (ROOT / "data" / "aso" / "aso_full.jsonl", "aso"),
    ]

    total_stats: list[dict[str, Any]] = []
    for input_path, source_type in inputs:
        if not input_path.exists():
            print(f"ATLA: {input_path} (yok)")
            continue
        output_path = input_path.parent / f"{input_path.stem}_clean{input_path.suffix}"
        report_path = input_path.parent / f"{input_path.stem}_report.json"
        print(f"İşleniyor: {input_path} ({source_type})")
        stats = process_file(input_path, output_path, report_path, source_type)
        total_stats.append(stats)
        print(f"  Toplam: {stats['toplam_kayit']}, Temiz: {stats['temizlenen']}, Duzen: {stats['duzenlenen']}")

    # Özet rapor
    summary_path = ROOT / "data" / "quality" / "veri_temizleme_ozet.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {"files": total_stats, "zaman": datetime.now(timezone.utc).isoformat(timespec="seconds")},
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nÖzet: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
