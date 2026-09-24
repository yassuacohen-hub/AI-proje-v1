# -*- coding: utf-8 -*-
"""PO-BACK-08: Executive Dashboard v1 — MRR/ARR, churn ve tenant sağlığı.

Bu ekran yönetici sorusunu tek bakışta yanıtlar:
"Yinelenen gelir ne kadar?", "Müşteri kaybı hangi düzeyde?" ve
"Tenant'larım hangi sağlık bandında?" Hesaplar Streamlit'ten bağımsız
``company_master.executive_ozet`` modülünde; burada yalnızca veri yükleme ve
çizim yapılır.

Kurallar
--------
- **Sayfa iskeleti sözleşmesi (ADMIN-UI-09/10):** başlık `PageHeader`, gövde
  `Section` blokları ile kurulur. ``st.subheader`` ya da elle yazılmış markdown
  başlık **kullanılmaz** (bkz. ``tests/test_sayfa_iskeleti.py``).
- **Zarif düşüş:** DB erişilemezse ekran boş veriyle çizilir, Plotly kurulu
  değilse trend ``st.line_chart`` ile gösterilir. Executive ekranı hiçbir
  koşulda patlamaz.
- **Tek fiyat kaynağı:** paket fiyatları ``company_master.paketler``
  (PO-BACK-04) üzerinden okunur; bu dosyada fiyat sabiti tutulmaz.
- **Tek KPI dili (ADMIN-EXEC-01):** metrikler ``st.metric`` değil
  ``web_dashboard.charts.kpi_karti`` ile çizilir (ADMIN-KPI-KART kalıbı).
- **Sessiz except yok (ADMIN-EXEC-01):** veri yükleme hatası yutulmaz;
  ``hata`` alanında taşınır, ekranda ``hata_kutusu`` ile gösterilir ve
  ``logging`` ile kayda geçer (ADMIN-HATA kalıbı).
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from company_master.executive_ozet import (
    churn_orani,
    health_dagilimi,
    mrr_arr,
    mrr_trend,
)
from company_master.tenant.health import hesapla as _saglik_hesapla
from company_master.tenant.model import VARSAYILAN_TENANT
from company_master.ui import PageHeader, Section, hata_kutusu
from company_master.ui.charts import line_chart
from web_dashboard.charts import kpi_karti  # noqa: E402  (ADMIN-EXEC-01)
from web_dashboard.tabs._db_yardim import tablo_var_mi

logger = logging.getLogger(__name__)

#: Trend serisinin uzunluğu (ay).
TREND_AY_SAYISI = 6

#: Tenant sağlığı için taranacak en fazla firma sayısı (performans sınırı).
SAGLIK_ORNEK_LIMITI = 1000

#: Churn penceresi (gün).
CHURN_GUN = 90

#: Sağlık bandı → (etiket, kpi kategorisi). Sıra ekrandaki kolon sırasıdır.
SAGLIK_BANTLARI: tuple[tuple[str, str, str], ...] = (
    ("green", "🟢 Sağlıklı", "basari"),
    ("yellow", "🟡 Uyarı", "uyari"),
    ("red", "🔴 Kritik", "tehlike"),
)


@st.cache_data(ttl=60)
def load_executive_ozet() -> dict[str, Any]:
    """Executive özet verisini hazırlar (abonelikler + tenant sağlığı).

    Abonelikler ``company_packages`` (firma-paket atama) ile ``packages``
    tablosunun birleşiminden okunur; tenant sağlığı örnek bir firma
    kümesinden ``tenant/health.py`` ile **tüketilerek** hesaplanır.

    Returns:
        ``{"abonelikler": [...], "tenantlar": [...], "kaynak": "db"|"bos",
        "hata": str|None, "tenant_hata": str|None}``
        DB erişilemezse boş listeler, ``kaynak="bos"`` ve ``hata`` metni döner
        (hata yutulmaz; ekran ``hata_kutusu`` ile gösterir, log'a yazılır).
    """
    sonuc: dict[str, Any] = {
        "abonelikler": [],
        "tenantlar": [],
        "kaynak": "bos",
        "hata": None,
        "tenant_hata": None,
        "veri_yok": False,
    }

    try:
        engine = get_engine()
    except Exception as exc:  # noqa: BLE001 — zarif düşüş; hata görünür kalır
        logger.warning("Executive abonelik verisi okunamadı: %s", exc)
        sonuc["hata"] = f"{type(exc).__name__}: {exc}"
        return sonuc

    # UI-ADMIN-SAHTE-EXEC-02: her iki tablo da yoksa sahte 0 yerine rozet.
    # inspect() gerçek olmayan (test) engine'lerde kullanılamazsa eski
    # davranışa düşülür (sorgu denenir, hata varsa normal akış yakalar).
    try:
        tablo_yok = not tablo_var_mi("packages", engine) or not tablo_var_mi(
            "company_packages", engine
        )
    except Exception:
        tablo_yok = False
    if tablo_yok:
        sonuc["veri_yok"] = True
        sonuc["hata"] = "packages / company_packages tablosu DB'de yok"
        return sonuc

    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT p.name AS paket, p.price AS aylik_ucret, "
                    "cp.assigned_at AS baslangic, cp.status AS durum "
                    "FROM company_packages cp "
                    "JOIN packages p ON p.package_id = cp.package_id"
                )
            ).mappings().all()
        sonuc["abonelikler"] = [dict(row) for row in rows]
        sonuc["kaynak"] = "db"
    except Exception as exc:  # noqa: BLE001 — zarif düşüş; hata görünür kalır
        logger.warning("Executive abonelik verisi okunamadı: %s", exc)
        sonuc["hata"] = f"{type(exc).__name__}: {exc}"
        return sonuc

    try:
        sonuc["tenantlar"] = [_tenant_sagligi(engine)]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Executive tenant sağlığı hesaplanamadı: %s", exc)
        sonuc["tenant_hata"] = f"{type(exc).__name__}: {exc}"

    return sonuc


def _tl(deger: Any, ondalik: int = 0) -> str:
    """Parayı Türkçe biçimde yazar: ``12.345 ₺`` (biçimlenemezse ``—``).

    ``i18n.sayi`` ile aynı kurala uyar: binlik ayraç `.`, ondalık ayraç ``,``.
    """
    try:
        ham = f"{float(deger):,.{ondalik}f}"
    except (TypeError, ValueError):
        return "—"
    return ham.replace(",", "#").replace(".", ",").replace("#", ".") + " ₺"


def _firma_kayitlari(engine: Any) -> list[dict[str, Any]]:
    """Sağlık hesabı için örnek firma kayıtlarını üretir.

    Alan adları ``tenant/health.py`` sözleşmesine çevrilir: ``address_line`` →
    ``adres``; ``updated_at`` → ``son_guncelleme_gun`` (yalnızca son 30 gün
    içinde güncellenenler dolu sayılır, tazelik metriği bu alanı okur).
    """
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT data_quality_score, nace_code, "
                "address_line AS adres, updated_at "
                "FROM companies WHERE is_ankara = TRUE LIMIT :limit"
            ),
            {"limit": SAGLIK_ORNEK_LIMITI},
        ).mappings().all()

    esik = datetime.now() - timedelta(days=30)
    kayitlar: list[dict[str, Any]] = []
    for row in rows:
        guncelleme = row.get("updated_at")
        if isinstance(guncelleme, str):
            try:
                guncelleme = datetime.fromisoformat(guncelleme.replace("Z", "+00:00"))
            except ValueError:
                guncelleme = None
        taze = guncelleme if isinstance(guncelleme, datetime) else None
        kayitlar.append(
            {
                "data_quality_score": row.get("data_quality_score") or 0,
                "nace_code": row.get("nace_code"),
                "adres": row.get("adres"),
                "son_guncelleme_gun": (
                    (datetime.now() - taze).days
                    if taze is not None and taze >= esik
                    else None
                ),
            }
        )
    return kayitlar


def _tenant_sagligi(engine: Any) -> dict[str, Any]:
    """Varsayılan tenant'ın sağlık skorunu sözlük olarak döndürür.

    ``health.py`` **değiştirilmez**; yalnız ``hesapla()`` çağrılır ve çıktısı
    (``TenantHealthScore``) ``to_dict()`` ile serileştirilir.
    """
    skor = _saglik_hesapla(VARSAYILAN_TENANT, _firma_kayitlari(engine))
    return skor.to_dict()


def _sayi_guvenli(deger: Any) -> float:
    """Değeri float'a çevirir; ``None``/bozuk girdi ``0.0`` sayılır."""
    try:
        return float(deger or 0)
    except (TypeError, ValueError):
        return 0.0


def _mrr_grafigi(seri: list[dict[str, Any]]) -> None:
    """MRR trendini çizgi grafik olarak çizer.

    Plotly kuruluysa ``st.plotly_chart``, değilse ``st.line_chart`` kullanılır
    (CHART-01 sözleşmesi: grafik yüzünden ekran asla patlamaz).
    """
    # mrr_trend boş abonelikte de 12 aylık sıfır serisi döndürür; sıfır çizgi
    # çizmek yerine boş durum gösterilir.
    if not seri or not any(_sayi_guvenli(satir.get("mrr")) for satir in seri):
        st.info("Trend grafiği için abonelik verisi bulunamadı.")
        return

    cerceve = pd.DataFrame(seri)
    fig = line_chart(cerceve.set_index("ay"), x="ay", y="mrr", title="MRR Trendi")
    st.plotly_chart(fig, width="stretch")


def _churn_donemi(gun: int = CHURN_GUN) -> tuple[str, str]:
    """Churn penceresini (son ``gun`` gün) ISO metin olarak döndürür."""
    bugun = datetime.now().date()
    return (bugun - timedelta(days=gun)).isoformat(), bugun.isoformat()


def _mrr_delta(seri: list[dict[str, Any]]) -> str | None:
    """Son iki ayın MRR farkını işaretli TL metni olarak döndürür (``+1.200 ₺``).

    Seri iki aydan kısaysa ya da son iki ayda hiç gelir yoksa ``None``
    (kartta delta satırı çizilmez; boş veride "değişim yok" yanıltır).
    """
    if len(seri) < 2:
        return None
    try:
        son, onceki = float(seri[-1]["mrr"]), float(seri[-2]["mrr"])
    except (KeyError, TypeError, ValueError):
        return None
    if son == 0 and onceki == 0:
        return None
    fark = round(son - onceki, 2)
    if fark == 0:
        return f"{_tl(0)} (değişim yok)"
    return f"+{_tl(fark)}" if fark > 0 else _tl(fark)


def _hatalari_goster(veri: dict[str, Any]) -> None:
    """Yükleme hatalarını ``hata_kutusu`` ile ekrana taşır (sessiz düşüş yok)."""
    if veri.get("kaynak") != "db":
        hata_kutusu(
            "Abonelik verisine ulaşılamadı",
            veri.get("hata") or "DB bağlantısı kurulamadı",
            ipucu="Ekran boş veriyle çiziliyor. DATABASE_URL / Postgres servisini kontrol edin.",
        )
    if veri.get("tenant_hata"):
        hata_kutusu(
            "Tenant sağlığı hesaplanamadı",
            veri.get("tenant_hata"),
            ipucu="companies tablosu ve tenant/health.py girdileri kontrol edilmeli.",
        )


def render_executive_tab() -> None:
    """Executive Dashboard sekmesini çizer (MRR/ARR · churn · tenant sağlığı)."""
    PageHeader(
        "Executive Dashboard",
        "Yinelenen gelir, müşteri kaybı ve tenant sağlığını tek ekranda özetler.",
        ust_etiket="İş Operasyonları",
        ikon="📈",
    ).render()

    veri = load_executive_ozet()
    abonelikler = veri.get("abonelikler") or []
    tenantlar = veri.get("tenantlar") or []

    gelir = mrr_arr(abonelikler)
    seri = mrr_trend(abonelikler, TREND_AY_SAYISI)
    baslangic, bitis = _churn_donemi()
    churn = churn_orani(baslangic, bitis, abonelikler)
    dagilim = health_dagilimi(tenantlar)

    _hatalari_goster(veri)

    # --- 1) Üç ana metrik (kpi_karti — tek KPI dili) ----------------------
    Section(
        "Gelir Özeti",
        "Aktif aboneliklerden türetilen yinelenen gelir ve kayıp oranı.",
    ).render()

    veri_yok = bool(veri.get("veri_yok"))
    kolon1, kolon2, kolon3 = st.columns(3)
    with kolon1:
        kpi_karti(
            "MRR (Aylık Yinelenen Gelir)",
            "veri kaynağı yok" if veri_yok else _tl(gelir["mrr"]),
            delta=None if veri_yok else _mrr_delta(seri),
            ikon="⚠️" if veri_yok else "💰",
            kategori="uyari" if veri_yok else "basari",
            yardim="Aktif aboneliklerin aylık ücret toplamı; delta son iki ayın farkı.",
            anahtar="exec-mrr",
        )
    with kolon2:
        kpi_karti(
            "ARR (Yıllık Yinelenen Gelir)",
            "veri kaynağı yok" if veri_yok else _tl(gelir["arr"]),
            ikon="⚠️" if veri_yok else "📅",
            kategori="uyari" if veri_yok else "marka",
            yardim="MRR × 12.",
            anahtar="exec-arr",
        )
    with kolon3:
        kpi_karti(
            f"Churn Oranı ({CHURN_GUN} gün)",
            "veri kaynağı yok" if veri_yok else f"%{churn:.2f}".replace(".", ","),
            ikon="⚠️" if veri_yok else "📉",
            kategori="uyari" if veri_yok else ("tehlike" if churn > 0 else "bilgi"),
            yardim="Dönem başında aktif olup dönem içinde iptal edilen aboneliklerin payı.",
            anahtar="exec-churn",
        )

    if veri_yok:
        st.caption("ARPA (abonelik başına gelir): veri kaynağı yok")
    else:
        st.caption(
            f"Aktif abonelik: {gelir['aktif_abonelik']} · "
            f"Pasif: {gelir['pasif_abonelik']} · "
            f"ARPA (abonelik başına gelir): {_tl(gelir['arpa'])}"
        )

    if gelir["paket_dagilimi"]:
        st.dataframe(
            pd.DataFrame(
                sorted(gelir["paket_dagilimi"].items()),
                columns=["Paket", "Aktif Abonelik"],
            ),
            hide_index=True,
            width="stretch",
        )

    # --- 2) Trend grafiği -------------------------------------------------
    Section(
        "MRR Trendi",
        f"Son {TREND_AY_SAYISI} ayın yinelenen gelir seyri (aylık kesit).",
    ).render()
    _mrr_grafigi(seri)

    # --- 3) Tenant sağlık dağılımı ---------------------------------------
    Section(
        "Tenant Sağlık Dağılımı",
        "Tenant Health Score bantlarına göre tenant sayısı "
        "(yeşil ≥ 85 · sarı 60-84 · kırmızı < 60).",
    ).render()

    for kolon, (bant, etiket, kategori) in zip(st.columns(3), SAGLIK_BANTLARI):
        with kolon:
            kpi_karti(
                etiket,
                int(dagilim.get(bant, 0) or 0),
                kategori=kategori,
                yardim="Tenant Health Score bandındaki tenant sayısı.",
                anahtar=f"exec-saglik-{bant}",
            )

    toplam_tenant = sum(dagilim.values())
    if toplam_tenant == 0:
        st.caption("Sağlık skoru hesaplanabilen tenant bulunamadı.")
    else:
        st.caption(f"Toplam {toplam_tenant} tenant değerlendirildi.")


