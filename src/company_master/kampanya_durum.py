# -*- coding: utf-8 -*-
"""PO-BACK-03: Kampanya durum makinesi (saf mantık, DB bağımsız).

Durum akışı::

    taslak ──► planlandı ──► aktif ◄──► duraklatıldı
                  │            │             │
                  ▼            ▼             ▼
                iptal      tamamlandı      iptal
                               (uç)          (uç)

Kurallar:
- ``gecis_yap(mevcut, hedef)`` yalnızca izinli geçişlerde hedef durumu döner;
  aksi hâlde ``ValueError`` fırlatır (bilinmeyen durum dâhil).
- ``tamamlandı`` ve ``iptal`` uç durumlardır; çıkış yok.
- ``pazarlama.py`` içindeki ``status`` sütunu İngilizce değer taşır
  (``draft/scheduled/active/paused/completed/cancelled``); ``db_deger`` /
  ``db_degerden`` ile çift yönlü çevrilir. ``pazarlama.py``'ye dokunulmaz.
"""
from __future__ import annotations

from typing import Final, Mapping

TASLAK: Final = "taslak"
PLANLANDI: Final = "planlandı"
AKTIF: Final = "aktif"
DURAKLATILDI: Final = "duraklatıldı"
TAMAMLANDI: Final = "tamamlandı"
IPTAL: Final = "iptal"

DURUMLAR: Final[tuple[str, ...]] = (
    TASLAK, PLANLANDI, AKTIF, DURAKLATILDI, TAMAMLANDI, IPTAL,
)
BASLANGIC_DURUMU: Final = TASLAK
UC_DURUMLAR: Final[frozenset[str]] = frozenset({TAMAMLANDI, IPTAL})

_GECISLER: Final[Mapping[str, frozenset[str]]] = {
    TASLAK: frozenset({PLANLANDI, IPTAL}),
    PLANLANDI: frozenset({AKTIF, IPTAL}),
    AKTIF: frozenset({DURAKLATILDI, TAMAMLANDI, IPTAL}),
    DURAKLATILDI: frozenset({AKTIF, IPTAL}),
    TAMAMLANDI: frozenset(),
    IPTAL: frozenset(),
}

# pazarlama.py `campaigns.status` sütunuyla eşleme (Türkçe ↔ DB)
_DB_ESLEME: Final[Mapping[str, str]] = {
    TASLAK: "draft",
    PLANLANDI: "scheduled",
    AKTIF: "active",
    DURAKLATILDI: "paused",
    TAMAMLANDI: "completed",
    IPTAL: "cancelled",
}
_DB_TERS: Final[Mapping[str, str]] = {v: k for k, v in _DB_ESLEME.items()}


def durum_dogrula(durum: str) -> str:
    """Durumu normalize eder (kırp + küçük harf); bilinmiyorsa ValueError."""
    if not isinstance(durum, str):
        raise ValueError(f"Durum metin olmalı: {durum!r}")
    d = durum.strip().lower()
    if d not in _GECISLER:
        raise ValueError(f"Bilinmeyen durum: {durum!r}. İzinli: {', '.join(DURUMLAR)}")
    return d


def izinli_gecisler(durum: str | None = None) -> dict[str, tuple[str, ...]] | tuple[str, ...]:
    """Geçiş tablosu.

    - Parametresiz: ``{durum: (hedefler...)}`` tam tablo.
    - ``durum`` verilirse yalnız o durumun hedefleri (sıralı tuple).
    """
    if durum is None:
        return {d: tuple(sorted(_GECISLER[d], key=DURUMLAR.index)) for d in DURUMLAR}
    d = durum_dogrula(durum)
    return tuple(sorted(_GECISLER[d], key=DURUMLAR.index))


def gecis_izinli_mi(mevcut: str, hedef: str) -> bool:
    """Geçiş izinliyse True; bilinmeyen durumda ValueError."""
    return durum_dogrula(hedef) in _GECISLER[durum_dogrula(mevcut)]


def gecis_yap(mevcut: str, hedef: str) -> str:
    """İzinli geçişte hedef durumu döner; değilse ValueError."""
    m, h = durum_dogrula(mevcut), durum_dogrula(hedef)
    if h not in _GECISLER[m]:
        if m in UC_DURUMLAR:
            neden = f"'{m}' uç durumdur; çıkış yok"
        else:
            neden = f"'{m}' → '{h}' izinli değil. İzinli hedefler: {', '.join(_GECISLER[m]) or '-'}"
        raise ValueError(f"Geçersiz kampanya geçişi: {neden}")
    return h


def uc_durum_mu(durum: str) -> bool:
    """Durum uç (terminal) mu?"""
    return durum_dogrula(durum) in UC_DURUMLAR


def db_deger(durum: str) -> str:
    """Türkçe durum → ``campaigns.status`` DB değeri."""
    return _DB_ESLEME[durum_dogrula(durum)]


def db_degerden(status: str) -> str:
    """``campaigns.status`` DB değeri → Türkçe durum; bilinmiyorsa ValueError."""
    if not isinstance(status, str):
        raise ValueError(f"DB durumu metin olmalı: {status!r}")
    s = status.strip().lower()
    if s not in _DB_TERS:
        raise ValueError(f"Bilinmeyen DB durumu: {status!r}. İzinli: {', '.join(_DB_TERS)}")
    return _DB_TERS[s]


__all__ = [
    "TASLAK", "PLANLANDI", "AKTIF", "DURAKLATILDI", "TAMAMLANDI", "IPTAL",
    "DURUMLAR", "BASLANGIC_DURUMU", "UC_DURUMLAR",
    "durum_dogrula", "izinli_gecisler", "gecis_izinli_mi", "gecis_yap",
    "uc_durum_mu", "db_deger", "db_degerden",
]
