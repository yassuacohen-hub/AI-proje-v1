# -*- coding: utf-8 -*-
"""PO-BACK-08: Executive Dashboard v1 — yönetici özeti (MRR/ARR, churn, health).

Neden ayrı modül?
    Executive görünümü üç bağımsız soruyu tek ekranda yanıtlar:
    "Yinelenen gelirim ne kadar?" (:func:`mrr_arr`), "Müşteri kaybı hangi
    düzeyde?" (:func:`churn_orani`) ve "Tenant'larım hangi sağlık bandında?"
    (:func:`health_dagilimi`). Bu hesaplar Streamlit/DB'den bağımsız **saf
    fonksiyonlara** ayrıldı; panel çalıştırılmadan test edilebilir
    (bkz. ``tests/test_executive_ozet.py``).

Bağımlılık sözleşmesi
    - ``company_master.paketler.fiyat_katalogu()`` → paket fiyatlarının **tek
      kaynağıdır** (PO-BACK-04). Abonelik kaydında açık ücret yoksa fiyat
      buradan türetilir; bu modül içinde ikinci bir fiyat tablosu **tutulmaz**.
    - ``company_master.tenant.health`` yalnızca **tüketilir**: ``hesapla()``
      çıktısı (``TenantHealthScore``) ve bant eşikleri (``HEALTH_GREEN`` /
      ``HEALTH_YELLOW``) okunur; sağlık modülüne hiçbir zaman yazılmaz.

Girdi sözleşmesi — abonelik kaydı (``dict``)::

    {"paket": "Standart", "durum": "aktif", "baslangic": "2026-01-15",
     "bitis": None, "aylik_ucret": 2999.0}

    Alan adları esnektir; ilk dolu alan kazanır:
      - paket   : ``paket`` | ``package`` | ``paket_adi`` | ``paket_ad`` | ``plan``
      - ücret   : ``aylik_ucret`` | ``aylik_fiyat`` | ``mrr`` | ``ucret`` | ``price`` | ``fiyat``
      - başlama : ``baslangic`` | ``baslama`` | ``baslangic_tarihi`` | ``start`` | ``started_at``
      - bitiş   : ``bitis`` | ``iptal_tarihi`` | ``bitis_tarihi`` | ``end`` | ``ended_at`` | ``cancelled_at``
      - durum   : ``durum`` | ``status`` | ``state``

Hata politikası
    Boş / bozuk / ``None`` girdi **hata fırlatmaz**; 0 ya da boş dağılım döner.
    Tek bir hatalı kayıt tüm executive ekranını düşürmemelidir.

Tüm parasal değerler TL, oranlar 0-100 arası ve 2 ondalığa yuvarlanır.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Iterable

from company_master.paketler import fiyat_katalogu
from company_master.tenant.health import HEALTH_GREEN, HEALTH_YELLOW

__all__ = [
    "AKTIF_DURUMLAR",
    "IPTAL_DURUMLARI",
    "BANTLAR",
    "abonelik_aktif_mi",
    "abonelik_ucreti",
    "paket_fiyatlari",
    "mrr_arr",
    "churn_orani",
    "health_dagilimi",
    "mrr_trend",
]

#: Aboneliğin "yürürlükte" sayıldığı durum değerleri (küçük harfe indirgenir).
AKTIF_DURUMLAR: frozenset[str] = frozenset(
    {"aktif", "active", "onayli", "onaylı", "deneme", "trial", "yeni"}
)

#: Aboneliğin kapandığını bildiren durum değerleri.
IPTAL_DURUMLARI: frozenset[str] = frozenset(
    {
        "iptal",
        "iptal_edildi",
        "iptal edildi",
        "cancelled",
        "canceled",
        "churn",
        "pasif",
        "inactive",
        "sonlandi",
        "sonlandı",
    }
)

#: Sağlık bantları — ``tenant/health.py`` ile aynı sözlük (green/yellow/red).
BANTLAR: tuple[str, str, str] = ("green", "yellow", "red")

# --- Alan adı adayları (esnek girdi) ---------------------------------------
_PAKET_ALANLARI: tuple[str, ...] = ("paket", "package", "paket_adi", "paket_ad", "plan")
_UCRET_ALANLARI: tuple[str, ...] = (
    "aylik_ucret",
    "aylik_fiyat",
    "mrr",
    "ucret",
    "price",
    "fiyat",
)
_BASLANGIC_ALANLARI: tuple[str, ...] = (
    "baslangic",
    "baslama",
    "baslangic_tarihi",
    "start",
    "started_at",
)
_BITIS_ALANLARI: tuple[str, ...] = (
    "bitis",
    "iptal_tarihi",
    "bitis_tarihi",
    "end",
    "ended_at",
    "cancelled_at",
    "sonlandirma_tarihi",
)
_DURUM_ALANLARI: tuple[str, ...] = ("durum", "status", "state")


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

def _alan(kayit: dict[str, Any], adaylar: Iterable[str]) -> Any:
    """Kayıtta ilk **dolu** alanı döndürür (esnek alan adı sözleşmesi)."""
    for ad in adaylar:
        if ad in kayit:
            deger = kayit[ad]
            if deger is None:
                continue
            if isinstance(deger, str) and not deger.strip():
                continue
            return deger
    return None


def _sayi(deger: Any) -> float:
    """Değeri negatif olmayan ``float``a çevirir; çevrilemezse 0.0."""
    if isinstance(deger, bool) or deger is None:
        return 0.0
    if isinstance(deger, (int, float)):
        return max(0.0, float(deger))
    if isinstance(deger, str):
        temiz = deger.strip().replace(" ", "")
        # "2.999,00" / "2999.00" / "2999" — Türkçe ve İngilizce ayraç desteği
        if "," in temiz and "." in temiz:
            temiz = temiz.replace(".", "").replace(",", ".")
        elif "," in temiz:
            temiz = temiz.replace(",", ".")
        try:
            return max(0.0, float(temiz))
        except ValueError:
            return 0.0
    return 0.0


def _tarih(deger: Any) -> date | None:
    """``date`` / ``datetime`` / ISO metni güvenli biçimde ``date``e çevirir.

    Çözümlenemeyen değer için ``None`` döner (istisna fırlatmaz).
    """
    if deger is None or isinstance(deger, bool):
        return None
    if isinstance(deger, datetime):
        return deger.date()
    if isinstance(deger, date):
        return deger
    if isinstance(deger, str):
        metin = deger.strip()
        if not metin:
            return None
        try:
            return datetime.fromisoformat(metin.replace("Z", "+00:00")).date()
        except ValueError:
            # "15.01.2026" / "15/01/2026" gibi TR biçimleri
            for ayrac in (".", "/"):
                parcalar = metin.split(ayrac)
                if len(parcalar) == 3:
                    try:
                        gun, ay, yil = (int(p) for p in parcalar)
                        return date(yil, ay, gun)
                    except (ValueError, TypeError):
                        continue
            return None
    return None


def paket_fiyatlari() -> dict[str, float]:
    """Paket adı → aylık fiyat (PO-BACK-04 tek fiyat kaynağından türetilir).

    ``fiyat_katalogu()`` çağrısı her seferinde yapılır; böylece testlerde
    katalog monkeypatch edildiğinde modül güncel değeri görür.
    """
    katalog: dict[str, float] = {}
    for paket in fiyat_katalogu():
        if not isinstance(paket, dict):
            continue
        ad = str(paket.get("name") or "").strip()
        if ad:
            katalog[ad] = _sayi(paket.get("price"))
    return katalog


def abonelik_ucreti(abonelik: dict[str, Any]) -> float:
    """Aboneliğin **aylık** ücreti.

    Öncelik: kayıttaki açık ücret alanı → paket adından katalog fiyatı.
    İkisi de yoksa 0.0 (bilinmeyen fiyat sessizce sıfır sayılır).
    """
    if not isinstance(abonelik, dict):
        return 0.0
    acik = _alan(abonelik, _UCRET_ALANLARI)
    if acik is not None:
        return _sayi(acik)
    paket = _alan(abonelik, _PAKET_ALANLARI)
    if paket is None:
        return 0.0
    return paket_fiyatlari().get(str(paket).strip(), 0.0)


def abonelik_aktif_mi(abonelik: dict[str, Any]) -> bool:
    """Abonelik yürürlükte mi?

    Kural (sırayla):
      1. Durum ``IPTAL_DURUMLARI`` içindeyse → ``False``.
      2. Bitiş tarihi geçmişse (bugünden önceyse) → ``False``.
      3. Durum ``AKTIF_DURUMLAR`` içindeyse → ``True``.
      4. Durum yok/bilinmiyorsa: bitiş tarihi yok ya da gelecekte → ``True``
         (kayıt "hâlâ yürürlükte" varsayılır; eksik alan cezalandırılmaz).
    """
    if not isinstance(abonelik, dict):
        return False
    durum = str(_alan(abonelik, _DURUM_ALANLARI) or "").strip().lower()
    if durum in IPTAL_DURUMLARI:
        return False
    bitis = _tarih(_alan(abonelik, _BITIS_ALANLARI))
    if bitis is not None and bitis < date.today():
        return False
    return True


# ---------------------------------------------------------------------------
# 1) MRR / ARR
# ---------------------------------------------------------------------------

def _kayitlar(abonelikler: Any) -> list[dict[str, Any]]:
    """Girdiyi güvenli ``dict`` listesine indirger (bozuk kayıtlar atılır)."""
    if not abonelikler:
        return []
    return [a for a in abonelikler if isinstance(a, dict)]


def mrr_arr(abonelikler: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Aktif aboneliklerden MRR/ARR (ve ARPA) hesaplar.

    MRR = aktif aboneliklerin aylık ücretleri toplamı.
    ARR = MRR × 12.
    ARPA (Average Revenue Per Account) = MRR / aktif abonelik sayısı.

    Args:
        abonelikler: Abonelik kayıtları (bkz. modül dokümanı). ``None`` olabilir.

    Returns:
        ``{"mrr", "arr", "arpa", "aktif_abonelik", "pasif_abonelik",
        "toplam_abonelik", "paket_dagilimi"}``

    Example:
        >>> mrr_arr([{"paket": "Temel", "durum": "aktif"}])["mrr"]
        499.0
    """
    kayitlar = _kayitlar(abonelikler)
    aktifler = [a for a in kayitlar if abonelik_aktif_mi(a)]
    mrr = round(sum(abonelik_ucreti(a) for a in aktifler), 2)
    adet = len(aktifler)

    paket_dagilimi: dict[str, int] = {}
    for abonelik in aktifler:
        ham = _alan(abonelik, _PAKET_ALANLARI)
        anahtar = str(ham).strip() if ham is not None else "bilinmeyen"
        if not anahtar:
            anahtar = "bilinmeyen"
        paket_dagilimi[anahtar] = paket_dagilimi.get(anahtar, 0) + 1

    return {
        "mrr": mrr,
        "arr": round(mrr * 12, 2),
        "arpa": round(mrr / adet, 2) if adet else 0.0,
        "aktif_abonelik": adet,
        "pasif_abonelik": len(kayitlar) - adet,
        "toplam_abonelik": len(kayitlar),
        "paket_dagilimi": paket_dagilimi,
    }


# ---------------------------------------------------------------------------
# 2) Churn (müşteri kaybı)
# ---------------------------------------------------------------------------

def _donem_gecerli(baslangic: date | None, bitis: date | None) -> bool:
    """Dönem sınırları anlamlı mı? (ikisi de dolu ve ters değil)"""
    return baslangic is not None and bitis is not None and bitis >= baslangic


def _donem_basinda_aktif(abonelik: dict[str, Any], baslangic: date) -> bool:
    """Abonelik dönem başında yürürlükte miydi? (churn paydası)"""
    kayit_baslangic = _tarih(_alan(abonelik, _BASLANGIC_ALANLARI))
    if kayit_baslangic is not None and kayit_baslangic > baslangic:
        return False
    kayit_bitis = _tarih(_alan(abonelik, _BITIS_ALANLARI))
    return kayit_bitis is None or kayit_bitis >= baslangic


def churn_orani(
    donem_baslangic: Any,
    donem_bitis: Any,
    abonelikler: list[dict[str, Any]] | None = None,
) -> float:
    """Dönem içindeki abonelik kaybı oranı (yüzde, 0-100).

    Pay    = bitiş (iptal) tarihi dönem aralığına düşen abonelikler.
    Payda  = dönem başında yürürlükte olan abonelikler (dönem içinde iptal
             edilenler dâhil).

    Geçersiz/eksik/ters dönem ya da boş payda → ``0.0`` (bölme hatası yok).

    Args:
        donem_baslangic: Dönem başı (``date``/``datetime``/ISO metin).
        donem_bitis: Dönem sonu (dönem sonu **dâhil**).
        abonelikler: Abonelik kayıtları; verilmezse oran 0.0.

    Example:
        >>> kayitlar = [
        ...     {"paket": "Temel", "baslangic": "2025-01-01"},
        ...     {"paket": "Temel", "baslangic": "2025-01-01", "bitis": "2026-02-10"},
        ... ]
        >>> churn_orani("2026-01-01", "2026-03-31", kayitlar)
        50.0
    """
    baslangic = _tarih(donem_baslangic)
    bitis = _tarih(donem_bitis)
    if not _donem_gecerli(baslangic, bitis):
        return 0.0

    kayitlar = _kayitlar(abonelikler)
    payda = [a for a in kayitlar if _donem_basinda_aktif(a, baslangic)]  # type: ignore[arg-type]
    if not payda:
        return 0.0

    pay = 0
    for abonelik in payda:
        kayit_bitis = _tarih(_alan(abonelik, _BITIS_ALANLARI))
        if kayit_bitis is not None and baslangic <= kayit_bitis <= bitis:  # type: ignore[operator]
            pay += 1
    return round(pay * 100.0 / len(payda), 2)


# ---------------------------------------------------------------------------
# 3) Tenant sağlık dağılımı
# ---------------------------------------------------------------------------

def _bandi_coz(tenant: Any) -> str | None:
    """Tenant kaydından sağlık bandını çıkarır; bilinemiyorsa ``None``.

    Sıra: açık ``band`` alanı → skor (``overall_score`` / ``overall`` / ``skor``)
    üzerinden ``tenant/health.py`` eşikleriyle hesaplama. Sağlık modülüne
    yazılmaz; yalnız ``HEALTH_GREEN`` / ``HEALTH_YELLOW`` sabitleri okunur.
    """
    band: Any = None
    skor: Any = None

    if isinstance(tenant, dict):
        band = tenant.get("band") or tenant.get("saglik_bandi") or tenant.get("health_band")
        for alan in ("overall_score", "overall", "skor", "score"):
            if tenant.get(alan) is not None:
                skor = tenant.get(alan)
                break
    else:
        band = getattr(tenant, "band", None)
        for alan in ("overall", "overall_score", "skor"):
            if getattr(tenant, alan, None) is not None:
                skor = getattr(tenant, alan)
                break

    if isinstance(band, str) and band.strip().lower() in BANTLAR:
        return band.strip().lower()

    try:
        deger = float(skor)
    except (TypeError, ValueError):
        return None
    if deger >= HEALTH_GREEN:
        return "green"
    if deger >= HEALTH_YELLOW:
        return "yellow"
    return "red"


def health_dagilimi(tenantlar: list[Any] | None) -> dict[str, int]:
    """Tenant'ların sağlık bandı dağılımı: ``{"green": n, "yellow": n, "red": n}``.

    Girdi esnektir: ``TenantHealthScore`` nesneleri, ``to_dict()`` çıktıları ya
    da yalnız ``band`` / ``overall_score`` taşıyan sözlükler. Bantı çözülemeyen
    kayıtlar **sayılmaz** (toplam dışı kalır, istisna fırlatılmaz).

    Üç bant anahtarı **her zaman** döner (0 olsa bile); böylece UI tarafında
    ``KeyError`` riski yoktur.

    Example:
        >>> health_dagilimi([{"band": "green"}, {"overall_score": 40}])
        {'green': 1, 'yellow': 0, 'red': 1}
    """
    dagilim: dict[str, int] = {bant: 0 for bant in BANTLAR}
    for tenant in tenantlar or []:
        bant = _bandi_coz(tenant)
        if bant is not None:
            dagilim[bant] += 1
    return dagilim


# ---------------------------------------------------------------------------
# 4) MRR trendi (executive çizgi grafiğinin verisi)
# ---------------------------------------------------------------------------

def _ay_kaydir(ay_basi: date, fark: int) -> date:
    """Ayın ilk gününü ``fark`` ay ileri/geri kaydırır (yıl devrini yönetir)."""
    toplam = (ay_basi.year * 12 + (ay_basi.month - 1)) + fark
    return date(toplam // 12, toplam % 12 + 1, 1)


def mrr_trend(
    abonelikler: list[dict[str, Any]] | None,
    ay_sayisi: int = 6,
    referans: Any = None,
) -> list[dict[str, Any]]:
    """Son ``ay_sayisi`` ayın MRR serisi (eskiden yeniye sıralı).

    Her ay için o ay **yürürlükte olan** aboneliklerin aylık ücretleri toplanır.
    Aylık ücret abonelik başına sabit kabul edilir (kademeli fiyat değişimi
    bu sürümün kapsamı dışındadır).

    Args:
        abonelikler: Abonelik kayıtları.
        ay_sayisi: Serideki ay sayısı (≤0 → boş liste).
        referans: Serinin bittiği tarih (varsayılan: bugün). Test için enjekte
            edilebilir — böylece test "bugüne" bağlı kırılgan olmaz.

    Returns:
        ``[{"ay": "2026-04", "mrr": 12345.67, "aktif_abonelik": 3}, ...]``
    """
    try:
        ay_adedi = int(ay_sayisi)
    except (TypeError, ValueError):
        return []
    if ay_adedi <= 0:
        return []

    bugun = _tarih(referans) or date.today()
    kayitlar = _kayitlar(abonelikler)
    son_ay = bugun.replace(day=1)

    seri: list[dict[str, Any]] = []
    for geri in range(ay_adedi - 1, -1, -1):
        baslangic = _ay_kaydir(son_ay, -geri)
        bitis = _ay_kaydir(baslangic, 1) - timedelta(days=1)
        toplam = 0.0
        adet = 0
        for abonelik in kayitlar:
            kayit_baslangic = _tarih(_alan(abonelik, _BASLANGIC_ALANLARI))
            kayit_bitis = _tarih(_alan(abonelik, _BITIS_ALANLARI))
            if kayit_baslangic is not None and kayit_baslangic > bitis:
                continue
            if kayit_bitis is not None and kayit_bitis < baslangic:
                continue
            toplam += abonelik_ucreti(abonelik)
            adet += 1
        seri.append(
            {
                "ay": f"{baslangic.year:04d}-{baslangic.month:02d}",
                "mrr": round(toplam, 2),
                "aktif_abonelik": adet,
            }
        )
    return seri





