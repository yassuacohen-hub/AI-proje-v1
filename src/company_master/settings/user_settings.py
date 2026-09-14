# -*- coding: utf-8 -*-
"""P7-46: Kullanıcı ayarları servisi.

Tasarım ilkeleri:
- **Streamlit'ten bağımsız**: saf Python; testte UI gerekmez.
- **Şema odaklı**: her ayar `AyarTanimi` ile tanımlanır; panel formu bu şemadan üretilir.
- **Güvenli yazma**: atomik dosya yazımı (önce .tmp, sonra os.replace).
- **Kullanıcı izolasyonu**: her kullanıcı kendi dosyasında (`data/user_settings/<id>.json`).
- **Bozuk dosyaya dayanıklı**: JSON okunamazsa varsayılanlara düşer, çökmez.

Ayarlar UI temasıyla (UX-03 `theme.js`) uyumludur: `tema` değeri
`dark | light | sistem` kümesinden gelir.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

__all__ = [
    "AYAR_SEMASI",
    "AyarHatasi",
    "AyarTanimi",
    "ayar_kaydet",
    "ayarlari_getir",
    "ayarlari_sifirla",
    "ayarlari_yaz",
    "dogrula",
    "gruplar",
    "varsayilanlar",
]

_KOK: Final[Path] = Path(__file__).resolve().parents[3]
VARSAYILAN_DIZIN: Final[Path] = _KOK / "data" / "user_settings"

#: Kullanıcı kimliğinde izin verilen karakterler (path traversal koruması).
_KIMLIK_RX: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._@-]{1,64}$")


class AyarHatasi(ValueError):
    """Geçersiz ayar değeri veya geçersiz kullanıcı kimliği."""


@dataclass(frozen=True)
class AyarTanimi:
    """Tek bir ayarın şema tanımı.

    Args:
        anahtar: Ayarın benzersiz adı (JSON anahtarı).
        etiket: Panelde gösterilen Türkçe başlık.
        tip: "secim" | "bool" | "sayi" | "metin".
        varsayilan: Şema varsayılanı.
        grup: Panelde sekmelendirme için grup adı.
        secenekler: `tip="secim"` için izinli değerler.
        alt_sinir/ust_sinir: `tip="sayi"` için kapalı aralık.
        aciklama: Panelde yardım metni.
    """

    anahtar: str
    etiket: str
    tip: str
    varsayilan: Any
    grup: str
    secenekler: tuple[Any, ...] = field(default_factory=tuple)
    alt_sinir: int | None = None
    ust_sinir: int | None = None
    aciklama: str = ""


AYAR_SEMASI: Final[tuple[AyarTanimi, ...]] = (
    # --- Görünüm ---
    AyarTanimi(
        anahtar="tema",
        etiket="Tema",
        tip="secim",
        varsayilan="sistem",
        grup="Görünüm",
        secenekler=("sistem", "dark", "light"),
        aciklama="Panel renk teması. 'sistem' işletim sistemi tercihini izler.",
    ),
    AyarTanimi(
        anahtar="yogun_mod",
        etiket="Yoğun (kompakt) mod",
        tip="bool",
        varsayilan=False,
        grup="Görünüm",
        aciklama="Satır yüksekliklerini daraltır; ekrana daha fazla kayıt sığar.",
    ),
    AyarTanimi(
        anahtar="sayfa_boyutu",
        etiket="Sayfa başına kayıt",
        tip="sayi",
        varsayilan=50,
        grup="Görünüm",
        alt_sinir=10,
        ust_sinir=500,
        aciklama="Tablolarda tek sayfada gösterilecek kayıt sayısı (10-500).",
    ),
    AyarTanimi(
        anahtar="varsayilan_bolum",
        etiket="Açılış bölümü",
        tip="secim",
        varsayilan="ana_kontrol",
        grup="Görünüm",
        secenekler=("ana_kontrol", "musteriler", "kalite", "sistem", "yonetim"),
        aciklama="Panel açıldığında gösterilecek bölüm.",
    ),
    # --- Veri ---
    AyarTanimi(
        anahtar="otomatik_yenileme",
        etiket="Otomatik yenileme",
        tip="bool",
        varsayilan=False,
        grup="Veri",
        aciklama="Panel verisini belirli aralıkla kendiliğinden tazeler.",
    ),
    AyarTanimi(
        anahtar="yenileme_araligi",
        etiket="Yenileme aralığı (sn)",
        tip="secim",
        varsayilan=30,
        grup="Veri",
        secenekler=(15, 30, 60, 300, 600),
        aciklama="Otomatik yenileme açıkken iki tazeleme arasındaki süre.",
    ),
    AyarTanimi(
        anahtar="kvkk_maskeleme",
        etiket="KVKK maskeleme",
        tip="bool",
        varsayilan=True,
        grup="Veri",
        aciklama="Telefon ve e-posta alanlarını maskeli gösterir. Kapatmak yetki gerektirir.",
    ),
    AyarTanimi(
        anahtar="disa_aktarim_bicimi",
        etiket="Dışa aktarım biçimi",
        tip="secim",
        varsayilan="csv",
        grup="Veri",
        secenekler=("csv", "xlsx", "json"),
        aciklama="İndirme düğmelerinin öntanımlı dosya biçimi.",
    ),
    # --- Bildirim ---
    AyarTanimi(
        anahtar="bildirim_eposta",
        etiket="E-posta bildirimi",
        tip="bool",
        varsayilan=False,
        grup="Bildirim",
        aciklama="Kritik uyarılar için e-posta gönderilsin.",
    ),
    AyarTanimi(
        anahtar="bildirim_telegram",
        etiket="Telegram bildirimi",
        tip="bool",
        varsayilan=False,
        grup="Bildirim",
        aciklama="Kritik uyarılar için Telegram mesajı gönderilsin.",
    ),
    AyarTanimi(
        anahtar="bildirim_esigi",
        etiket="Bildirim eşiği",
        tip="secim",
        varsayilan="kritik",
        grup="Bildirim",
        secenekler=("bilgi", "uyari", "kritik"),
        aciklama="Bu seviyeden düşük olaylar bildirim üretmez.",
    ),
    # --- Bölgesel ---
    AyarTanimi(
        anahtar="dil",
        etiket="Arayüz dili",
        tip="secim",
        varsayilan="tr",
        grup="Bölgesel",
        secenekler=("tr", "en"),
        aciklama="Panel metin dili.",
    ),
    AyarTanimi(
        anahtar="saat_dilimi",
        etiket="Saat dilimi",
        tip="secim",
        varsayilan="Europe/Istanbul",
        grup="Bölgesel",
        secenekler=("Europe/Istanbul", "UTC"),
        aciklama="Tarih/saat alanlarının gösterim dilimi.",
    ),
)

_SEMA_HARITASI: Final[dict[str, AyarTanimi]] = {t.anahtar: t for t in AYAR_SEMASI}


def gruplar() -> dict[str, list[AyarTanimi]]:
    """Şemayı panel sekmeleri için grup adına göre kümeler (tanım sırası korunur)."""
    cikti: dict[str, list[AyarTanimi]] = {}
    for tanim in AYAR_SEMASI:
        cikti.setdefault(tanim.grup, []).append(tanim)
    return cikti


def varsayilanlar() -> dict[str, Any]:
    """Şemadaki tüm ayarların varsayılan değerlerini döndürür."""
    return {t.anahtar: t.varsayilan for t in AYAR_SEMASI}


def _kimlik_dogrula(kullanici_id: str) -> str:
    """Kullanıcı kimliğini doğrular (dizin dışına çıkışı engeller)."""
    if not isinstance(kullanici_id, str) or not _KIMLIK_RX.match(kullanici_id):
        raise AyarHatasi(f"Geçersiz kullanıcı kimliği: {kullanici_id!r}")
    return kullanici_id


def _dosya_yolu(kullanici_id: str, dizin: Path | None = None) -> Path:
    """Kullanıcının ayar dosyasının tam yolu."""
    kok = Path(dizin) if dizin is not None else VARSAYILAN_DIZIN
    return kok / f"{_kimlik_dogrula(kullanici_id)}.json"


def dogrula(anahtar: str, deger: Any) -> Any:
    """Tek bir ayarı şemaya göre doğrular ve normalize edilmiş değeri döndürür.

    Raises:
        AyarHatasi: Anahtar şemada yoksa veya değer şemaya uymuyorsa.
    """
    tanim = _SEMA_HARITASI.get(anahtar)
    if tanim is None:
        raise AyarHatasi(f"Bilinmeyen ayar: {anahtar!r}")

    if tanim.tip == "bool":
        if not isinstance(deger, bool):
            raise AyarHatasi(f"{anahtar}: mantıksal (True/False) değer bekleniyor")
        return deger

    if tanim.tip == "sayi":
        # bool, int'in alt sınıfıdır; sayı alanına bool sızmasını engelle.
        if isinstance(deger, bool) or not isinstance(deger, int):
            raise AyarHatasi(f"{anahtar}: tam sayı bekleniyor")
        if tanim.alt_sinir is not None and deger < tanim.alt_sinir:
            raise AyarHatasi(f"{anahtar}: en az {tanim.alt_sinir} olmalı")
        if tanim.ust_sinir is not None and deger > tanim.ust_sinir:
            raise AyarHatasi(f"{anahtar}: en fazla {tanim.ust_sinir} olmalı")
        return deger

    if tanim.tip == "secim":
        if deger not in tanim.secenekler:
            izinli = ", ".join(str(s) for s in tanim.secenekler)
            raise AyarHatasi(f"{anahtar}: geçersiz seçim {deger!r} (izinli: {izinli})")
        return deger

    if tanim.tip == "metin":
        if not isinstance(deger, str):
            raise AyarHatasi(f"{anahtar}: metin bekleniyor")
        return deger.strip()

    raise AyarHatasi(f"{anahtar}: bilinmeyen tip {tanim.tip!r}")


def _atomik_yaz(yol: Path, metin: str) -> None:
    """Atomik metin yazma: geçici dosyaya yaz, fsync, sonra yerine taşı."""
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(yol.parent),
        prefix=f".{yol.name}.",
        suffix=".tmp",
        delete=False,
    )
    try:
        with gecici as f:
            f.write(metin)
            f.flush()
            os.fsync(f.fileno())
        os.replace(gecici.name, yol)
    except Exception:
        try:
            os.unlink(gecici.name)
        except OSError:
            pass
        raise


def ayarlari_getir(kullanici_id: str, dizin: Path | None = None) -> dict[str, Any]:
    """Kullanıcının ayarlarını döndürür; eksik/bozuk alanlar varsayılana düşer.

    Dosya yoksa, okunamıyorsa veya bozuk JSON içeriyorsa çökmez — varsayılanları verir.
    Şemada olmayan eski anahtarlar sessizce atılır (şema evrilebilir).
    """
    sonuc = varsayilanlar()
    yol = _dosya_yolu(kullanici_id, dizin)
    try:
        ham = json.loads(yol.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return sonuc
    if not isinstance(ham, dict):
        return sonuc

    for anahtar, deger in ham.items():
        try:
            sonuc[anahtar] = dogrula(anahtar, deger)
        except AyarHatasi:
            continue  # bilinmeyen ya da bozuk alan: varsayılanda kal
    return sonuc


def ayarlari_yaz(
    kullanici_id: str,
    degerler: dict[str, Any],
    dizin: Path | None = None,
) -> dict[str, Any]:
    """Birden çok ayarı doğrulayıp toplu kaydeder (hepsi-ya-hiç).

    Herhangi bir değer geçersizse hiçbiri yazılmaz.

    Returns:
        Kayıt sonrası ayarların tamamı.
    """
    if not isinstance(degerler, dict):
        raise AyarHatasi("Ayar sözlüğü bekleniyor")

    dogrulanmis = {anahtar: dogrula(anahtar, deger) for anahtar, deger in degerler.items()}

    mevcut = ayarlari_getir(kullanici_id, dizin)
    mevcut.update(dogrulanmis)

    yol = _dosya_yolu(kullanici_id, dizin)
    _atomik_yaz(yol, json.dumps(mevcut, ensure_ascii=False, indent=2, sort_keys=True))
    return mevcut


def ayar_kaydet(
    kullanici_id: str,
    anahtar: str,
    deger: Any,
    dizin: Path | None = None,
) -> dict[str, Any]:
    """Tek bir ayarı doğrulayıp kaydeder."""
    return ayarlari_yaz(kullanici_id, {anahtar: deger}, dizin)


def ayarlari_sifirla(kullanici_id: str, dizin: Path | None = None) -> dict[str, Any]:
    """Kullanıcının ayarlarını şema varsayılanlarına döndürür (dosyayı siler)."""
    yol = _dosya_yolu(kullanici_id, dizin)
    try:
        yol.unlink()
    except OSError:
        pass
    return varsayilanlar()
