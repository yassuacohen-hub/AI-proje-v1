"""NACE kodu eşleştirme ve zenginleştirme modülü.

NACE Rev. 2 (Türkiye uyarlaması) 4-haneli alt sınıf kodları üzerinden
firma → sektör eşleştirmesi yapar. Üç katmanlı veri kaynağı:

- data/nace_rev2_tr.json — NACE hiyerarşisi (4 hane, ~60-100 yaygın alt sınıf)
- data/nace_to_ostim_sektor.json — OSTİM 17 sektör eşleştirme tablosu
- Gelecekte: MERSİS'den otomatik NACE çekimi (Karar 9)

Karar referansı: V10/10_ankara_osb_sentez.md Karar 9 (yeni, 2026-09-01).

Tasarım ilkeleri (AGENTS.md):
- Tip güvenliği: dataclass + type hints.
- Hata yönetimi: dosya yoksa anlamlı FileNotFoundError, JSON bozuksa ValueError.
- Modüler: her fonksiyon tek sorumluluk (SRP).
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DATA_DIR: Path = Path(__file__).resolve().parents[3] / "data"

NACE_TAXONOMY_FILE: Path = DATA_DIR / "nace_rev2_tr.json"
OSTIM_MAPPING_FILE: Path = DATA_DIR / "nace_to_ostim_sektor.json"

TURKISH_DEACCENT_MAP: dict[str, str] = {
    "ı": "i", "İ": "i", "ş": "s", "Ş": "s",
    "ğ": "g", "Ğ": "g", "ü": "u", "Ü": "u",
    "ö": "o", "Ö": "o", "ç": "c", "Ç": "c",
}


@dataclass
class NaceRecord:
    """Tek bir NACE alt sınıfı için zenginleştirilmiş kayıt.

    Attributes:
        code: 4-haneli NACE kodu (ör. "25.11").
        name_tr: Türkçe açıklama.
        section: Bölüm harfi (ör. "C").
        section_name: Bölüm adı (ör. "İmalat").
        relevance: MERSİS'ten geldiyse "Yüksek", tahminse "Yüksek/Orta/Düşük".
        keywords: Eşleştirme için anahtar kelimeler.
        matched_ostim_sectors: Eşleşen OSTİM sektör isimleri.
    """
    code: str
    name_tr: str
    section: str = ""
    section_name: str = ""
    relevance: str = "Orta"
    keywords: list[str] = field(default_factory=list)
    matched_ostim_sectors: list[str] = field(default_factory=list)


def _read_json(path: Path) -> dict | list:
    """JSON dosyasını UTF-8 (BOM'suz) olarak okur.

    Args:
        path: Mutlak dosya yolu.

    Returns:
        JSON içeriği (dict veya list).

    Raises:
        FileNotFoundError: Dosya yoksa.
        ValueError: JSON parse hatası.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"NACE veri dosyası bulunamadı: {path}. "
            f"Beklenen konum: {path.absolute()}"
        )
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"NACE JSON dosyası bozuk: {path} — {exc}"
        ) from exc


def _flatten_subclasses(data: dict) -> list[dict]:
    """Hiyerarşik NACE JSON'unu alt-sınıf düzeyinde düzleştirir."""
    rows: list[dict] = []
    for section_code, section in data.items():
        section_name = section.get("name_tr", "")
        for _group_code, group in section.get("groups", {}).items():
            for _class_code, cls in group.get("classes", {}).items():
                for sub_code, sub_name in cls.get("subclasses", {}).items():
                    rows.append({
                        "code": sub_code,
                        "name_tr": sub_name,
                        "section": section_code,
                        "section_name": section_name,
                    })
    return rows


def load_nace_taxonomy() -> list[NaceRecord]:
    """data/nace_rev2_tr.json dosyasından NACE hiyerarşisini yükler.

    Returns:
        NACE alt sınıfları (NaceRecord listesi). Hiyerarşi bozuksa boş liste döner.
    """
    try:
        data = _read_json(NACE_TAXONOMY_FILE)
    except FileNotFoundError:
        logger.warning("NACE taxonomy dosyası yok, boş liste döndürülüyor.")
        return []
    except ValueError as exc:
        logger.error("NACE taxonomy parse hatası: %s", exc)
        return []

    if isinstance(data, list):
        rows = data
    else:
        rows = _flatten_subclasses(data)

    return [
        NaceRecord(
            code=row["code"],
            name_tr=row.get("name_tr", ""),
            section=row.get("section", ""),
            section_name=row.get("section_name", ""),
            keywords=row.get("keywords", []),
            matched_ostim_sectors=row.get("matched_ostim_sectors", []),
            relevance=row.get("relevance", "Orta"),
        )
        for row in rows
    ]


def load_ostim_mapping() -> dict[str, dict]:
    """OSTİM sektör → NACE eşleştirme tablosunu yükler."""
    try:
        data = _read_json(OSTIM_MAPPING_FILE)
    except FileNotFoundError:
        logger.warning("OSTİM eşleştirme dosyası yok, boş dict döndürülüyor.")
        return {}
    except ValueError as exc:
        logger.error("OSTİM eşleştirme parse hatası: %s", exc)
        return {}
    return data


def _normalize_tr(text: str) -> str:
    """Türkçe karakterleri ASCII karşılığına çevirip küçültür."""
    if not text:
        return ""
    out = []
    for ch in text:
        out.append(TURKISH_DEACCENT_MAP.get(ch, ch))
    return "".join(out).lower()


def _keyword_match(keyword: str, normalized_text: str) -> bool:
    """Kelime sınırı ile Türkçe anahtar kelime eşleştirmesi."""
    if not keyword or not normalized_text:
        return False
    kw_norm = _normalize_tr(keyword)
    if " " in kw_norm:
        return kw_norm in normalized_text
    pattern = r"\b" + re.escape(kw_norm) + r"\b"
    return re.search(pattern, normalized_text) is not None


def nace_bul(
    unvan: str,
    mevcut_nace: Optional[str] = None,
    ostim_sektor: Optional[str] = None,
) -> list[NaceRecord]:
    """Firma adı + sektör bilgisinden NACE kodu tahmin eder.

    Args:
        unvan: Firma ünvanı (ör. "Demir Çelik San. Tic. Ltd. Şti.").
        mevcut_nace: MERSİS'den gelen NACE (varsa öncelikli, Yüksek güven).
        ostim_sektor: OSTİM sektörü (varsa filtre).

    Returns:
        Tahmin edilen NACE kodları (max 5), relevance sıralı.
        MERSİS varsa tek kayıt, Yüksek güvenle döner.
    """
    if mevcut_nace:
        return [
            NaceRecord(
                code=mevcut_nace,
                name_tr="(MERSİS'den)",
                section="",
                section_name="(MERSİS)",
                relevance="Yüksek",
            )
        ]

    if not unvan:
        return []

    unvan_norm = _normalize_tr(unvan)
    ostim_map = load_ostim_mapping()
    matches: list[NaceRecord] = []

    if ostim_sektor and ostim_sektor in ostim_map:
        nace_codes = ostim_map[ostim_sektor].get("nace_codes", [])
        for entry in nace_codes:
            keywords = entry.get("keywords", [])
            if any(_keyword_match(kw, unvan_norm) for kw in keywords):
                matches.append(
                    NaceRecord(
                        code=entry["code"],
                        name_tr=entry.get("name_tr", ""),
                        relevance=entry.get("relevance", "Orta"),
                        matched_ostim_sectors=[
                            ostim_map[ostim_sektor].get("sektor", ostim_sektor)
                        ],
                    )
                )
    else:
        taxonomy = load_nace_taxonomy()
        for record in taxonomy:
            for kw in record.keywords:
                if _keyword_match(kw, unvan_norm):
                    matches.append(record)
                    break

    relevance_order = {"Yüksek": 0, "Orta": 1, "Düşük": 2}
    matches.sort(key=lambda r: relevance_order.get(r.relevance, 99))
    return matches[:5]


def nace_to_ostim_sektorler(nace_code: str) -> list[str]:
    """Verilen NACE kodundan eşleşen OSTİM sektör isimlerini döndürür.

    Args:
        nace_code: 4-haneli NACE kodu (ör. "25.11").

    Returns:
        OSTİM sektör isimleri listesi.
    """
    if not nace_code:
        return []
    ostim_map = load_ostim_mapping()
    matched: list[str] = []
    for sektor_data in ostim_map.values():
        for entry in sektor_data.get("nace_codes", []):
            if entry.get("code") == nace_code:
                sektor_adi = sektor_data.get("sektor", "")
                if sektor_adi and sektor_adi not in matched:
                    matched.append(sektor_adi)
    return matched


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    taxonomy = load_nace_taxonomy()
    print(f"NACE alt sınıf sayısı: {len(taxonomy)}")

    ostim_map = load_ostim_mapping()
    print(f"OSTİM sektör eşleştirme: {len(ostim_map)} sektör")

    test_firmalar = [
        ("Demir Çelik Konstrüksiyon A.Ş.", None, "Yapı ve İnşaat"),
        ("Oto Yedek Parça Tic. Ltd. Şti.", None, "Otomotiv"),
        ("CNC Tezgah İmalatı San.", None, "Makine ve Makine Ekipmanları"),
        ("Premium Yazılım A.Ş.", None, "Teknoloji ve Bilişim"),
        ("ABC Medikal Ltd. Şti.", None, "Sağlık"),
        ("Ankara Lojistik A.Ş.", "52.10", None),
    ]

    for unvan, nace, sektor in test_firmalar:
        matches = nace_bul(unvan, nace, sektor)
        print(f"\n{unvan}")
        for m in matches:
            print(f"  → {m.code}: {m.name_tr} ({m.relevance})")