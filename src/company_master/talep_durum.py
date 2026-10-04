# -*- coding: utf-8 -*-
"""TSG-05: Sorgu talebi durum makinesi + SLA hesabı (saf mantık, DB bağımsız).

Durum akışı::

    rezerve ──► işleniyor ──► tamam  (uç)
        │            │
        └────────────┴──────► iade   (uç)

Neden ayrı modül: `kampanya_durum.py` **kampanya** akışını tutar (taslak→aktif→
tamamlandı); talebin akışı farklıdır (rezerve→işleniyor→tamam/iade) ve uç
durumları başkadır. Aynı dosyaya iki tablo koymak `durum_dogrula()`'yı hangi
tabloya bakacağını bilmez hâle getirirdi. Desen kopyalanmadı, **aynısı korundu**
ki iki durum makinesi arasında öğrenilecek ikinci bir kullanım olmasın (K-1).

SLA (ürün sahibi kararı, 2026-09-29):
- Talep **mesai içinde** geldiyse son teslim = geliş + 10 dakika.
- Mesai dışında geldiyse son teslim = **ertesi iş günü** mesai başlangıcı + 10 dk.
- Hafta sonu ve mesai dışı saat aynı kuralla ertesi iş gününe taşınır.

ÖLÇÜLMEDİ (D-268): resmî tatil takvimi **yok**. `is_gunu_mu()` yalnız hafta
sonunu bilir; 29 Ekim'de gelen talebin SLA'i yanlış hesaplanır. `ponytail:`
tatil listesi ürün sahibinden gelince `_TATILLER` kümesi doldurulur ve
`is_gunu_mu()` onu da sorar — çağıran hiçbir yer değişmez.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Final, Mapping

REZERVE: Final = "rezerve"
ISLENIYOR: Final = "işleniyor"
TAMAM: Final = "tamam"
IADE: Final = "iade"

DURUMLAR: Final[tuple[str, ...]] = (REZERVE, ISLENIYOR, TAMAM, IADE)
BASLANGIC_DURUMU: Final = REZERVE
UC_DURUMLAR: Final[frozenset[str]] = frozenset({TAMAM, IADE})

_GECISLER: Final[Mapping[str, frozenset[str]]] = {
    REZERVE: frozenset({ISLENIYOR, IADE}),
    ISLENIYOR: frozenset({TAMAM, IADE}),
    TAMAM: frozenset(),
    IADE: frozenset(),
}

#: `sorgu_talepleri.durum` sütunuyla eşleme (Türkçe ↔ DB). Türkçe değerde
#: `ş`/`ı` var; DB'de ASCII tutulur ki indeks/sorgu kodlama sürprizi olmasın.
_DB_ESLEME: Final[Mapping[str, str]] = {
    REZERVE: "reserved",
    ISLENIYOR: "processing",
    TAMAM: "done",
    IADE: "refunded",
}
_DB_TERS: Final[Mapping[str, str]] = {v: k for k, v in _DB_ESLEME.items()}

#: Mesai penceresi (ürün sahibi kararı). Cumartesi/Pazar iş günü değildir.
MESAI_BASLANGIC: Final[time] = time(9, 0)
MESAI_BITIS: Final[time] = time(18, 0)
SLA_DAKIKA: Final[int] = 10

#: ponytail: resmî tatil takvimi ölçülmedi; küme bilerek boş (D-268).
#: Dolduğunda `is_gunu_mu()` otomatik kullanır, çağıran değişmez.
_TATILLER: Final[frozenset[date]] = frozenset()


def durum_dogrula(durum: str) -> str:
    """Durumu normalize eder (kırp + küçük harf); bilinmiyorsa ValueError."""
    if not isinstance(durum, str):
        raise ValueError(f"Durum metin olmalı: {durum!r}")
    d = durum.strip().lower()
    if d not in _GECISLER:
        raise ValueError(f"Bilinmeyen talep durumu: {durum!r}. İzinli: {', '.join(DURUMLAR)}")
    return d


def izinli_gecisler(durum: str | None = None) -> dict[str, tuple[str, ...]] | tuple[str, ...]:
    """Geçiş tablosu; parametresiz tam tablo, `durum` verilirse o durumun hedefleri."""
    if durum is None:
        return {d: tuple(sorted(_GECISLER[d], key=DURUMLAR.index)) for d in DURUMLAR}
    return tuple(sorted(_GECISLER[durum_dogrula(durum)], key=DURUMLAR.index))


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
            izinli = ", ".join(sorted(_GECISLER[m], key=DURUMLAR.index)) or "-"
            neden = f"'{m}' → '{h}' izinli değil. İzinli hedefler: {izinli}"
        raise ValueError(f"Geçersiz talep geçişi: {neden}")
    return h


def uc_durum_mu(durum: str) -> bool:
    """Durum uç (terminal) mu?"""
    return durum_dogrula(durum) in UC_DURUMLAR


def db_deger(durum: str) -> str:
    """Türkçe durum → `sorgu_talepleri.durum` DB değeri."""
    return _DB_ESLEME[durum_dogrula(durum)]


def db_degerden(durum: str) -> str:
    """DB değeri → Türkçe durum; bilinmiyorsa ValueError."""
    if not isinstance(durum, str):
        raise ValueError(f"DB durumu metin olmalı: {durum!r}")
    d = durum.strip().lower()
    if d not in _DB_TERS:
        raise ValueError(f"Bilinmeyen DB talep durumu: {durum!r}. İzinli: {', '.join(_DB_TERS)}")
    return _DB_TERS[d]


def is_gunu_mu(gun: date) -> bool:
    """Hafta içi ve tatil listesinde değil mi? (Tatil listesi henüz boş — D-268.)"""
    return gun.weekday() < 5 and gun not in _TATILLER


def mesai_icinde_mi(an: datetime) -> bool:
    """Verilen an mesai penceresinde mi? (İş günü + 09:00–18:00.)"""
    return is_gunu_mu(an.date()) and MESAI_BASLANGIC <= an.time() < MESAI_BITIS


def sla_son_teslim(gelis: datetime, sla_dakika: int = SLA_DAKIKA) -> datetime:
    """Talebin son teslim anı (ürün sahibi kuralı).

    - Mesai içinde: `gelis + sla_dakika`.
    - Mesai dışında: **ertesi iş günü** mesai başlangıcı + `sla_dakika`.

    `gelis` mesai içinde ama bitişe `sla_dakika`'dan az kalmışsa **taşınmaz** —
    kural "mesai içinde 10 dk" der, "10 dk mesai içinde biter" demez. Bu yönü
    uydurmak ürün sahibinin kararını genişletmek olurdu (ölçülmedi, sorulmadı).
    """
    if not isinstance(gelis, datetime):
        raise ValueError(f"Geliş anı datetime olmalı: {gelis!r}")
    if sla_dakika < 0:
        raise ValueError(f"SLA dakikası negatif olamaz: {sla_dakika}")
    if mesai_icinde_mi(gelis):
        return gelis + timedelta(minutes=sla_dakika)
    # Mesai dışı: aynı gün mesai başlamadan geldiyse o gün, yoksa sonraki iş günü.
    if is_gunu_mu(gelis.date()) and gelis.time() < MESAI_BASLANGIC:
        gun = gelis.date()
    else:
        gun = gelis.date() + timedelta(days=1)
        while not is_gunu_mu(gun):
            gun += timedelta(days=1)
    baslangic = datetime.combine(gun, MESAI_BASLANGIC, tzinfo=gelis.tzinfo)
    return baslangic + timedelta(minutes=sla_dakika)


def sla_asildi_mi(gelis: datetime, simdi: datetime, durum: str) -> bool:
    """Talep SLA'i aştı mı? Uç durumdaki talep aşmış sayılmaz (iş bitmiş)."""
    if uc_durum_mu(durum):
        return False
    return simdi > sla_son_teslim(gelis)


__all__ = [
    "REZERVE", "ISLENIYOR", "TAMAM", "IADE",
    "DURUMLAR", "BASLANGIC_DURUMU", "UC_DURUMLAR",
    "MESAI_BASLANGIC", "MESAI_BITIS", "SLA_DAKIKA",
    "durum_dogrula", "izinli_gecisler", "gecis_izinli_mi", "gecis_yap",
    "uc_durum_mu", "db_deger", "db_degerden",
    "is_gunu_mu", "mesai_icinde_mi", "sla_son_teslim", "sla_asildi_mi",
]
