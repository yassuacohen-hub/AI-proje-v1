# -*- coding: utf-8 -*-
"""MRK-02e/02f — Huginn dil paketi: tek kaynaklı metin motoru.

Tasarım sözleşmesi (onaylı "Katman Ayrımı + Yolculuk" sentezi):

* **katman** — `veri` | `cerceve`
  - `veri`   : sayı, durum, hata kodu, menü etiketi, para, tarih, yasal uyarı.
               **Kuru, kesin, mitolojisiz.** Müşterinin karar verdiği hiçbir
               rakam veya hata mitolojik dile bürünmez.
  - `cerceve`: sayfa başlığı, boş durum, ipucu, yükleme, başarı, onboarding.
               Mitolojik ve anlatısal olabilir.
* **seviye** — yalnız `cerceve` katmanında geçerlidir: `cirak` (uzun, öğretici)
  veya `usta` (kısa). `en` dili tek varyanttır, asla obje değildir.
* **ton** — `info | success | warning | danger | neutral` (bkz. `ton.py`).
  Ton, katmandan bağımsızdır (diktir).

Kaynak dosyalar:
  * ``ses.json`` — marka sesi (105 kayıt, tamamı `cerceve`).
  * ``ui.json``  — işlevsel arayüz (menü, eylem, durum, hata) + H1 üst etiketleri.

Kullanım::

    from company_master.i18n import t, ses, sayi, tarih

    t("menu_kpi")                      # "KPI Özeti"
    t("veri_sonuc_sayisi", sayi=42)    # "42 kayıt listeleniyor."
    t("huginn_liste_bos", seviye="usta")
    ses("odin_baglanti_koptu").ton     # "danger"
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

from company_master.i18n.ton import (
    VARSAYILAN_TON,
    TonHatasi,
    ton_dogrula,
    ton_ikon,
    ton_streamlit,
    ton_varyant,
)

__all__ = [
    "DILLER",
    "SEVIYELER",
    "KATMANLAR",
    "Metin",
    "I18nHatasi",
    "ParametreHatasi",
    "t",
    "ses",
    "sayi",
    "tarih",
    "dil_ayarla",
    "seviye_ayarla",
    "aktif_dil",
    "aktif_seviye",
    "anahtarlar",
    "sozluk",
    "onbellek_temizle",
    # ton köprüsü (tek içe aktarma noktası)
    "ton_dogrula",
    "ton_varyant",
    "ton_ikon",
    "ton_streamlit",
    "TonHatasi",
]

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

KOK: Final[Path] = Path(__file__).resolve().parent
KAYNAK_DOSYALAR: Final[tuple[str, ...]] = ("ses.json", "ui.json")

DILLER: Final[tuple[str, ...]] = ("tr", "en")
SEVIYELER: Final[tuple[str, ...]] = ("cirak", "usta")
KATMANLAR: Final[tuple[str, ...]] = ("veri", "cerceve")

VARSAYILAN_DIL: Final[str] = "tr"
VARSAYILAN_SEVIYE: Final[str] = "usta"

#: Meta anahtarlar (``_aciklama`` gibi) sözlüğe alınmaz.
META_ONEK: Final[str] = "_"

_aktif_dil: str = VARSAYILAN_DIL
_aktif_seviye: str = VARSAYILAN_SEVIYE


# ---------------------------------------------------------------------------
# Hatalar
# ---------------------------------------------------------------------------


class I18nHatasi(ValueError):
    """Dil paketi sözleşmesi ihlali."""


class ParametreHatasi(I18nHatasi):
    """Metindeki ``{param}`` yer tutucusu doldurulmadı.

    Sessizce ham metni döndürmek yerine açık hata veririz; aksi hâlde
    kullanıcıya ``"{sayi} kayıt listeleniyor."`` gibi bir metin sızar.
    """


# ---------------------------------------------------------------------------
# Çözümlenmiş metin kaydı
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Metin:
    """Tek bir anahtarın çözümlenmiş hâli.

    Attributes:
        anahtar: Sözlük anahtarı.
        metin: Dile ve seviyeye göre seçilmiş, parametreleri doldurulmuş metin.
        katman: ``veri`` veya ``cerceve``.
        ton: Beş tondan biri.
        ikon: Material Symbols adı (kayıtta yoksa tondan türetilir).
        dil: Metnin gerçekten alındığı dil (fallback sonrası).
        bulundu: Anahtar sözlükte var mıydı?
    """

    anahtar: str
    metin: str
    katman: str
    ton: str
    ikon: str
    dil: str
    bulundu: bool

    @property
    def varyant(self) -> str:
        """UI bileşen varyantı (``neutral`` → ``secondary``)."""
        return ton_varyant(self.ton)

    @property
    def streamlit_tipi(self) -> str:
        """`st.info` / `st.success` / `st.warning` / `st.error` seçimi."""
        return ton_streamlit(self.ton)

    def __str__(self) -> str:  # pragma: no cover - ince sarmalayıcı
        return self.metin


# ---------------------------------------------------------------------------
# Sözlük yükleme
# ---------------------------------------------------------------------------


def _dosya_oku(yol: Path) -> dict[str, Any]:
    if not yol.exists():
        raise I18nHatasi(f"Dil kaynağı bulunamadı: {yol}")
    with open(yol, encoding="utf-8") as f:
        veri = json.load(f)
    if not isinstance(veri, dict):
        raise I18nHatasi(f"Dil kaynağı sözlük değil: {yol}")
    return veri


@lru_cache(maxsize=1)
def sozluk() -> dict[str, dict[str, Any]]:
    """Tüm kaynak dosyaları birleştirip önbelleğe alır.

    Returns:
        ``{anahtar: kayit}`` biçiminde birleşik sözlük.

    Raises:
        I18nHatasi: Kaynak dosya yoksa, bozuksa veya aynı anahtar iki dosyada
            birden tanımlıysa.
    """
    birlesik: dict[str, dict[str, Any]] = {}
    kaynagi: dict[str, str] = {}
    for ad in KAYNAK_DOSYALAR:
        veri = _dosya_oku(KOK / ad)
        for anahtar, kayit in veri.items():
            if anahtar.startswith(META_ONEK):
                continue
            if anahtar in birlesik:
                raise I18nHatasi(
                    f"Anahtar iki kaynakta birden tanımlı: {anahtar} "
                    f"({kaynagi[anahtar]} ve {ad})"
                )
            if not isinstance(kayit, dict):
                raise I18nHatasi(f"{ad}: '{anahtar}' kaydı sözlük değil.")
            birlesik[anahtar] = kayit
            kaynagi[anahtar] = ad
    if not birlesik:
        raise I18nHatasi("Dil sözlüğü boş.")
    return birlesik


def anahtarlar() -> tuple[str, ...]:
    """Sözlükteki tüm anahtarları alfabetik döndürür."""
    return tuple(sorted(sozluk()))


def onbellek_temizle() -> None:
    """Sözlük önbelleğini boşaltır (testler ve sıcak yeniden yükleme için)."""
    sozluk.cache_clear()
    _coz.cache_clear()


# ---------------------------------------------------------------------------
# Dil / seviye durumu
# ---------------------------------------------------------------------------


def dil_dogrula(dil: str) -> str:
    """Dil kodunu doğrular."""
    if dil not in DILLER:
        raise I18nHatasi(f"Bilinmeyen dil: {dil!r}. İzinli: {', '.join(DILLER)}")
    return dil


def seviye_dogrula(seviye: str) -> str:
    """Anlatım seviyesini doğrular."""
    if seviye not in SEVIYELER:
        raise I18nHatasi(
            f"Bilinmeyen seviye: {seviye!r}. İzinli: {', '.join(SEVIYELER)}"
        )
    return seviye


def dil_ayarla(dil: str) -> str:
    """Süreç genelinde varsayılan dili değiştirir."""
    global _aktif_dil
    _aktif_dil = dil_dogrula(dil)
    _coz.cache_clear()
    return _aktif_dil


def seviye_ayarla(seviye: str) -> str:
    """Süreç genelinde varsayılan anlatım seviyesini değiştirir."""
    global _aktif_seviye
    _aktif_seviye = seviye_dogrula(seviye)
    _coz.cache_clear()
    return _aktif_seviye


def aktif_dil() -> str:
    """Geçerli varsayılan dil."""
    return _aktif_dil


def aktif_seviye() -> str:
    """Geçerli varsayılan anlatım seviyesi."""
    return _aktif_seviye


# ---------------------------------------------------------------------------
# Çözümleme
# ---------------------------------------------------------------------------


def _metin_sec(deger: Any, seviye: str, anahtar: str, dil: str) -> str:
    """Düz metin veya ``{cirak, usta}`` objesinden doğru varyantı seçer.

    Seviye fallback: istenen → diğer seviye → düz string.
    """
    if isinstance(deger, str):
        return deger
    if isinstance(deger, dict):
        if dil == "en":
            raise I18nHatasi(
                f"'{anahtar}' için 'en' değeri obje olamaz; tek varyant zorunlu."
            )
        secim = deger.get(seviye)
        if isinstance(secim, str) and secim:
            return secim
        for yedek in SEVIYELER:
            alternatif = deger.get(yedek)
            if isinstance(alternatif, str) and alternatif:
                return alternatif
        raise I18nHatasi(f"'{anahtar}' kaydında kullanılabilir metin yok.")
    raise I18nHatasi(f"'{anahtar}' değeri metin ya da obje olmalı, {type(deger)!r} geldi.")


@lru_cache(maxsize=512)
def _coz(anahtar: str, dil: str, seviye: str) -> Metin:
    """Anahtarı çözümler (parametre doldurmadan). Önbelleklenir."""
    kayitlar = sozluk()
    kayit = kayitlar.get(anahtar)
    if kayit is None:
        # Bilinmeyen anahtar çökertmez; anahtarın kendisi görünür kalır ki
        # eksik çeviri ekranda hemen fark edilsin.
        return Metin(
            anahtar=anahtar,
            metin=anahtar,
            katman="veri",
            ton=VARSAYILAN_TON,
            ikon=ton_ikon(VARSAYILAN_TON),
            dil=dil,
            bulundu=False,
        )

    katman = kayit.get("katman", "cerceve")
    if katman not in KATMANLAR:
        raise I18nHatasi(f"'{anahtar}' katmanı geçersiz: {katman!r}")

    ton = ton_dogrula(kayit.get("ton", VARSAYILAN_TON))

    # Dil fallback: istenen dil → tr → anahtar
    secilen_dil = dil
    ham = kayit.get(dil)
    if ham in (None, ""):
        secilen_dil = VARSAYILAN_DIL
        ham = kayit.get(VARSAYILAN_DIL)
    if ham in (None, ""):
        raise I18nHatasi(f"'{anahtar}' için hiçbir dilde metin yok.")

    metin = _metin_sec(ham, seviye, anahtar, secilen_dil)
    if katman == "veri" and not isinstance(ham, str):
        raise I18nHatasi(
            f"'{anahtar}' `veri` katmanında; metin düz string olmalı, seviye varyantı olamaz."
        )

    return Metin(
        anahtar=anahtar,
        metin=metin,
        katman=katman,
        ton=ton,
        ikon=str(kayit.get("ikon") or ton_ikon(ton)),
        dil=secilen_dil,
        bulundu=True,
    )


def _parametre_doldur(kayit: Metin, parametreler: dict[str, Any]) -> Metin:
    """``{param}`` yer tutucularını doldurur; eksikse açık hata verir."""
    if "{" not in kayit.metin:
        if parametreler:
            # Fazladan parametre sessizce yutulmaz: yazım hatasını yakalarız.
            raise ParametreHatasi(
                f"'{kayit.anahtar}' metni parametre beklemiyor, "
                f"verilenler: {sorted(parametreler)}"
            )
        return kayit
    try:
        dolu = kayit.metin.format(**parametreler)
    except KeyError as exc:
        eksik = str(exc).strip("'\"")
        raise ParametreHatasi(
            f"'{kayit.anahtar}' metni '{eksik}' parametresini bekliyor; verilmedi."
        ) from exc
    except (IndexError, ValueError) as exc:
        raise ParametreHatasi(
            f"'{kayit.anahtar}' metni biçimlendirilemedi: {exc}"
        ) from exc
    return Metin(
        anahtar=kayit.anahtar,
        metin=dolu,
        katman=kayit.katman,
        ton=kayit.ton,
        ikon=kayit.ikon,
        dil=kayit.dil,
        bulundu=kayit.bulundu,
    )


def ses(
    anahtar: str,
    *,
    dil: str | None = None,
    seviye: str | None = None,
    **parametreler: Any,
) -> Metin:
    """Anahtarı tam kayıt olarak çözümler (metin + ton + ikon + katman).

    Args:
        anahtar: Sözlük anahtarı.
        dil: ``tr`` veya ``en``; verilmezse aktif dil.
        seviye: ``cirak`` veya ``usta``; verilmezse aktif seviye.
        **parametreler: Metindeki ``{param}`` yer tutucuları.

    Returns:
        Çözümlenmiş :class:`Metin` kaydı.

    Raises:
        I18nHatasi: Dil/seviye/katman/ton sözleşmesi ihlalinde.
        ParametreHatasi: Yer tutucu eksik veya fazla parametre verildiğinde.
    """
    d = dil_dogrula(dil) if dil is not None else _aktif_dil
    s = seviye_dogrula(seviye) if seviye is not None else _aktif_seviye
    return _parametre_doldur(_coz(anahtar, d, s), parametreler)


def t(
    anahtar: str,
    *,
    dil: str | None = None,
    seviye: str | None = None,
    **parametreler: Any,
) -> str:
    """Anahtarın görünen metnini döndürür.

    :func:`ses` ile aynı kuralları uygular, yalnız metni verir.

    Example:
        >>> t("menu_kpi")
        'KPI Özeti'
    """
    return ses(anahtar, dil=dil, seviye=seviye, **parametreler).metin


# ---------------------------------------------------------------------------
# Biçimleyiciler (MRK-02f) — tek kaynak; card.py bunu kullanır
# ---------------------------------------------------------------------------


def sayi(deger: Any, ondalik: int | None = None) -> str:
    """Sayıyı Türkçe biçimde döndürür (binlik `.`, ondalık `,`).

    Args:
        deger: `int`, `float`, `bool` veya metin.
        ondalik: Basamak sayısı. `None` ise `int` için 0, `float` için 1.

    Returns:
        Biçimlenmiş metin. Sayıya çevrilemeyen değer olduğu gibi döner.

    Example:
        >>> sayi(1234567)
        '1.234.567'
        >>> sayi(12.345, ondalik=2)
        '12,35'
    """
    if isinstance(deger, bool):
        return "Evet" if deger else "Hayır"
    if isinstance(deger, int):
        basamak = 0 if ondalik is None else ondalik
    elif isinstance(deger, float):
        basamak = 1 if ondalik is None else ondalik
    else:
        return str(deger)
    ham = f"{deger:,.{basamak}f}"
    # `,` ve `.` yer değiştirir: 1,234.5 → 1.234,5
    return ham.replace(",", "#").replace(".", ",").replace("#", ".")


def para(deger: Any, birim: str = "₺") -> str:
    """Parasal değeri Türkçe biçimde döndürür.

    Example:
        >>> para(1234.5)
        '1.234,50 ₺'
    """
    if not isinstance(deger, (int, float)) or isinstance(deger, bool):
        return str(deger)
    return f"{sayi(float(deger), ondalik=2)} {birim}"


#: Kısa Türkçe ay adları (tarih biçimleyici için).
AYLAR: Final[tuple[str, ...]] = (
    "Oca", "Şub", "Mar", "Nis", "May", "Haz",
    "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara",
)


def tarih(deger: Any, saat: bool = False, uzun: bool = False) -> str:
    """Tarihi Türkçe biçimde döndürür.

    Args:
        deger: `datetime`, `date` veya ISO 8601 metin.
        saat: `True` ise `HH:MM` eklenir.
        uzun: `True` ise ay adı yazıyla gelir (`14 Eyl 2026`).

    Returns:
        Biçimlenmiş metin. Çözümlenemeyen değer olduğu gibi döner.

    Example:
        >>> tarih("2026-09-14T18:30:00")
        '14.09.2026'
        >>> tarih("2026-09-14T18:30:00", saat=True, uzun=True)
        '14 Eyl 2026 18:30'
    """
    an = deger
    if isinstance(an, str):
        try:
            an = datetime.fromisoformat(an.replace("Z", "+00:00"))
        except ValueError:
            return deger
    if isinstance(an, datetime):
        gun, ay, yil = an.day, an.month, an.year
        saat_metni = f" {an.hour:02d}:{an.minute:02d}" if saat else ""
    elif isinstance(an, date):
        gun, ay, yil = an.day, an.month, an.year
        saat_metni = ""
    else:
        return str(deger)
    govde = f"{gun} {AYLAR[ay - 1]} {yil}" if uzun else f"{gun:02d}.{ay:02d}.{yil}"
    return govde + saat_metni
