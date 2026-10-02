# -*- coding: utf-8 -*-
"""Kenar üreticileri — Faz 3 Entity Graph (VERI-ENTITY-GRAPH-01).

SSOT: `yedekler/Huginn Data Insights (HUGIns).txt:756-774` (10 düğüm türü),
`:779` ("Şirket ekosistemini görselleştirmek."), `:837-839` ("Şirket ağ
haritası."), `:859-861` (Faz 3 = Entity Graph).
Şema: `migrations/0047_entity_graph.sql` (tablo + kanonik liste).

Üç kural:

1. **Girdisi olmayan kenar üretilmez, `strength` 0 yazılmaz.** D-249: "veri yok"
   ile "0" ayrı değerlerdir. `strength` ölçülemiyorsa `None` döner.
2. **`evidence` boş bırakılamaz.** D-260: kanıtsız iddia yazılmaz. Boş/boşluk
   `evidence` taşıyan kenar `KenarHatasi` ile reddedilir — DB'ye hiç uğramaz.
3. **Kenar yazan tek kapı `kenarlari_yaz()`.** D-256/2. Üreticiler LİSTE DÖNER,
   DB'ye yazmaz; böylece canlı yazım görev dışı kalır (D-238).

v0 kapsamı yalnız 2 türdür: `same_osb`, `nace_complementary`. Diğer 9 tür
kanonik listede yer alır ama üretilmez — kaynak veri yoktur (D-260).

KÖPRÜ (D-184 — karar ↔ kod ↔ test):
  Şema : src/company_master/schema/migrations/0047_entity_graph.sql
  Test : tests/test_entity_graph.py
  SSOT : yedekler/Huginn Data Insights (HUGIns).txt:756-774, :779, :837-839, :859-861
  Görev: plans/brief_yasu_VERI-ENTITY-GRAPH-01.md
  Hub  : hubs/OSINT_VERI_TOPLAMA_HUB.md ("Kapanan işler" satırı)
"""
from __future__ import annotations

import itertools
import logging
from typing import Iterable, Mapping, NamedTuple, Sequence

from sqlalchemy import text

from ..db.connection import get_engine

logger = logging.getLogger(__name__)

__all__ = [
    "EDGE_TYPES_V0",
    "EDGE_TYPES_SSOT",
    "KANONIK_EDGE_TYPES",
    "EDGE_TYPES",
    "STRENGTH_ARALIK",
    "KENAR",
    "KenarHatasi",
    "normalize",
    "dogrula",
    "osb_komsulari",
    "nace_tamamlayici",
    "kenarlari_yaz",
]

#: v0'da ÜRETİLEN iki kenar türü. Kaynakları mevcut ve ölçülmüş veri tablolarıdır.
#:   same_osb           <- companies.osb_id            (0001_core.sql:51)
#:   nace_complementary <- company_industries.nace_code (0002_relations.sql:70)
EDGE_TYPES_V0: tuple[str, ...] = ("same_osb", "nace_complementary")

#: SSOT'tan türetilen, v0'da ÜRETİLMEYEN türler (boş bırakılır — D-249).
#: SSOT'un 10 düğüm türünden "Şirket" (SSOT:756) kök düğümdür ve kenar türü
#: değildir; geri kalan 9 attribute tipi ikili kenar türetir.
EDGE_TYPES_SSOT: tuple[str, ...] = (
    "shared_domain",        # SSOT:758  Domain
    "shared_phone",         # SSOT:760  Telefon
    "shared_email",         # SSOT:761  E-posta
    "shared_social_media",  # SSOT:762  Sosyal Medya
    "shared_officer",       # SSOT:763  Yönetici
    "shared_partner",       # SSOT:765  Ortak
    "same_branch",          # SSOT:767  Şube
    "same_brand",           # SSOT:769  Marka
    "same_group_company",   # SSOT:771  Grup Şirketleri
)

#: Şemadaki kanonik liste (`ck_company_edges_edge_type`). 11 değer.
#: Brif Faz A madde 1 "10 tür" yazıyor; sayı yerine kanonik liste esas alınır
#: (D-260 — kanıta dayalı liste, varsayılan sayı değil).
KANONIK_EDGE_TYPES: tuple[str, ...] = EDGE_TYPES_V0 + EDGE_TYPES_SSOT

#: Geriye uyumluluk adı.
EDGE_TYPES = KANONIK_EDGE_TYPES

STRENGTH_ARALIK = (0.0, 100.0)


class KenarHatasi(ValueError):
    """Kanıtsız veya kanonik olmayan kenar. Yazmadan ÖNCE reddedilir."""


class KENAR(NamedTuple):
    """Tek bir yönsüz kenar. `company_a_id < company_b_id` normalize edilmiş."""

    company_a_id: str
    company_b_id: str
    edge_type: str
    evidence: str
    strength: float | None = None
    source: str = ""


def normalize(a_id: str, b_id: str) -> tuple[str, str]:
    """Yönsüz kenarın tek temsilini üretir: `(min, max)`.

    Kenar yönsüzdür; `(b, a)` verilmesi `(a, b)` ile aynı kenardır.
    Şemadaki `CHECK (company_a_id < company_b_id)` ile birebir uyumludur —
    burada normalize edilmemiş bir kenar yazılırsa DB reddeder.
    """
    a, b = str(a_id), str(b_id)
    if a == b:
        raise KenarHatasi(f"kenar ucu ayni olmaz (self-loop): {a}")
    return (a, b) if a < b else (b, a)


def dogrula(kenar: KENAR) -> KENAR:
    """Tek kenarı kanıt kurallarına karşı denetler. Bozuksa `KenarHatasi`."""
    if kenar.edge_type not in KANONIK_EDGE_TYPES:
        raise KenarHatasi(
            f"kanonik liste disi edge_type: {kenar.edge_type!r}; "
            f"izinli: {', '.join(KANONIK_EDGE_TYPES)}"
        )
    if not (kenar.evidence or "").strip():
        # D-260: kanıtsız kenar yazılmaz.
        raise KenarHatasi(
            f"evidence bos — kanıtsiz kenar yazılamaz (edge_type={kenar.edge_type})"
        )
    if kenar.strength is not None and not (
        STRENGTH_ARALIK[0] <= kenar.strength <= STRENGTH_ARALIK[1]
    ):
        raise KenarHatasi(
            f"strength aralik disi: {kenar.strength} (beklenen {STRENGTH_ARALIK})"
        )
    a, b = normalize(kenar.company_a_id, kenar.company_b_id)
    if (a, b) != (kenar.company_a_id, kenar.company_b_id):
        # Normalize edilmemiş kenar yazmak yönsüzlük kuralını ihlal eder.
        return KENAR(a, b, kenar.edge_type, kenar.evidence,
                     kenar.strength, kenar.source)
    return kenar


def osb_komsulari(
    sirketler: Sequence[Mapping],
    *,
    osb_adlari: Mapping[str, str] | None = None,
) -> list[KENAR]:
    """`same_osb` kenarları: aynı `osb_id`'yi paylaşan firma çiftleri.

    Girdi `companies` satırlarıdır; yalnız `company_id` ve `osb_id` okunur
    (kolon adı ölçülmüştür — 0001_core.sql:51). DB'ye YAZMAZ.

    `strength` ölçülemez: OSB üyeliği ikili bir gerçektir, sayısal bir
    yakınlık değil. Bu yüzden `None` döner (D-249 — 0 yazılmaz).

    `osb_adlari` verilirse `evidence` insan-okur ad yazar ("aynı OSB: Başkent
    OSB"). Verilmezse kanıt metni UUID'yi taşır; yine de BOŞ DEĞİLDİR.
    """
    adlar = osb_adlari or {}
    gruplar: dict[str, list[str]] = {}
    for s in sirketler:
        osb_id = s.get("osb_id")
        if not osb_id:
            continue                      # OSB üyesi değil → kenar yok
        gruplar.setdefault(str(osb_id), []).append(str(s.get("company_id")))

    kenarlar: list[KENAR] = []
    for osb_id, uyeler in gruplar.items():
        ad = adlar.get(str(osb_id), str(osb_id))
        for a, b in itertools.combinations(sorted(uyeler), 2):
            kenarlar.append(KENAR(
                a, b, "same_osb",
                f"ayni OSB: {ad}",
                None,                       # ölçülemiyor → None, 0 değil
                "kenarlar.py:osb_komsulari/companies.osb_id",
            ))
    return kenarlar


def nace_tamamlayici(
    sirketler: Sequence[Mapping],
    *,
    nace_ust: Mapping[str, str] | None = None,
) -> list[KENAR]:
    """`nace_complementary` kenarları: aynı NACE üst grubunu paylaşan çiftler.

    Girdi `company_industries` satırlarıdır; `company_id` + `nace_code` okunur
    (0002_relations.sql:70-76). DB'ye YAZMAZ.

    "Tamamlayıcı" kuralı: iki farklı firmanın NACE kodu aynı üst koda
    (`nace_codes.parent_code`) düşüyorsa birbirini tamamlayan üretim hattı
    parçası olabilirler. `nace_ust` verilmezse kural uygulanmaz ve liste BOŞ
    döner — tahminle kenar yazmak D-260 ihlalidir.

    `strength` ölçülemez → `None` (D-249).
    """
    if not nace_ust:
        return []                          # üst kod haritası yok → kenar kanıtsız

    gruplar: dict[str, dict[str, list[str]]] = {}
    for s in sirketler:
        nace_code = s.get("nace_code")
        ust = nace_ust.get(str(nace_code)) if nace_code else None
        if not ust:
            continue                      # üst kodu bilinmiyor → kenar kanıtsız
        # Aynı üst grupta aynı kodu paylaşan iki firma "tamamlayıcı" DEĞİLDİR
        # (aynı işi yapan rakiptir); ayrım KOD seviyesinde yapılır.
        kod_map = gruplar.setdefault(str(ust), {})
        kod_map.setdefault(str(nace_code), []).append(str(s.get("company_id")))

    kenarlar: list[KENAR] = []
    for ust, kod_map in gruplar.items():
        kodlar = sorted(kod_map)
        for kod_a, kod_b in itertools.combinations(kodlar, 2):
            for a in sorted(kod_map[kod_a]):
                for b in sorted(kod_map[kod_b]):
                    kenarlar.append(KENAR(
                        a, b, "nace_complementary",
                        f"NACE tamamlayici: {ust} altinda {kod_a} ve {kod_b}",
                        None,
                        "kenarlar.py:nace_tamamlayici/company_industries.nace_code",
                    ))
    return kenarlar


def kenarlari_yaz(kenarlar: Iterable[KENAR], *, engine=None) -> int:
    """TEK YAZMA KAPISI (D-256/2). `company_edges`'e yazan tek fonksiyon budur.

    - `ON CONFLICT DO NOTHING` ile idempotent: aynı kenar iki kez verilirse
      tablo TEK satır tutar.
    - Her kenar `dogrula()`'dan geçer; kanıtsız veya kanonik dışı kenar
      yazılmadan `KenarHatasi` ile reddedilir (D-260).
    - `strength` `None` ise SQL NULL gider; 0 yazılmaz (D-249).

    Döner: gerçekten eklenen satır sayısı.
    """
    satirlar = [dogrula(k) for k in kenarlar]
    if not satirlar:
        return 0

    eng = engine or get_engine()
    sql = text("""
        INSERT INTO company_edges
            (company_a_id, company_b_id, edge_type, evidence, strength, source)
        VALUES
            (:company_a_id, :company_b_id, :edge_type, :evidence, :strength, :source)
        ON CONFLICT DO NOTHING
    """)
    with eng.connect() as conn:
        eklenen = 0
        for k in satirlar:
            res = conn.execute(sql, {
                "company_a_id": k.company_a_id,
                "company_b_id": k.company_b_id,
                "edge_type": k.edge_type,
                "evidence": k.evidence,
                "strength": k.strength,       # None → NULL (D-249)
                "source": k.source or None,
            })
            eklenen += res.rowcount if res.rowcount and res.rowcount > 0 else 0
        conn.commit()
    logger.info("company_edges: %d kenar yazildi", eklenen)
    return eklenen
