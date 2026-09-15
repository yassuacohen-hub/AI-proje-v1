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
"""
from __future__ import annotations

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
from company_master.ui import PageHeader, Section

#: Trend serisinin uzunluğu (ay).
TREND_AY_SAYISI = 6

#: Tenant sağlığı için taranacak en fazla firma sayısı (performans sınırı).
SAGLIK_ORNEK_LIMITI = 1000


@st.cache_data(ttl=60)
def load_executive_ozet() -> dict[str, Any]:
    """Executive özet verisini hazırlar (abonelikler + tenant sağlığı).

    Abonelikler ``company_packages`` (firma-paket atama) ile ``packages``
    tablosunun birleşiminden okunur; tenant sağlığı örnek bir firma
    kümesinden ``tenant/health.py`` ile **tüketilerek** hesaplanır.

    Returns:
        ``{"abonelikler": [...], "tenantlar": [...], "kaynak": "db"|"bos"}``
        DB erişilemezse boş listeler ve ``kaynak="bos"`` döner.
    """
    abonelikler: list[dict[str, Any]] = []
    tenantlar: list[dict[str, Any]] = []
    kaynak = "bos"

    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT p.name AS paket, p.price AS aylik_ucret, "
                    "cp.assigned_at AS baslangic, cp.status AS durum "
                    "FROM company_packages cp "
                    "JOIN packages p ON p.package_id = cp.package_id"
                )
            ).mappings().all()
        abonelikler = [dict(row) for row in rows]
        kaynak = "db"
    except Exception:
        return {"abonelikler": [], "tenantlar": [], "kaynak": kaynak}

    try:
        tenantlar = [_tenant_sagligi(engine)]
    except Exception:
        tenantlar = []

    return {"abonelikler": abonelikler, "tenantlar": tenantlar, "kaynak": kaynak}


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


def _mrr_grafigi(seri: list[dict[str, Any]]) -> None:
    """MRR trendini çizgi grafik olarak çizer.

    Plotly kuruluysa ``st.plotly_chart``, değilse ``st.line_chart`` kullanılır
    (CHART-01 sözleşmesi: grafik yüzünden ekran asla patlamaz).
    """
    if not seri:
        st.info("Trend grafiği için abonelik verisi bulunamadı.")
        return

    cerceve = pd.DataFrame(seri)
    try:
        import plotly.graph_objects as go
    except Exception:
        st.line_chart(cerceve.set_index("ay")["mrr"])
        return

    grafik = go.Figure()
    grafik.add_trace(
        go.Scatter(
            x=cerceve["ay"],
            y=cerceve["mrr"],
            mode="lines+markers",
            name="MRR",
            line={"width": 3},
        )
    )
    grafik.update_layout(
        height=340,
        margin={"l": 10, "r": 10, "t": 30, "b": 10},
        yaxis_title="MRR (₺)",
        xaxis_title="Ay",
    )
    st.plotly_chart(grafik, use_container_width=True)


def _churn_donemi(gun: int = 90) -> tuple[str, str]:
    """Churn penceresini (son ``gun`` gün) ISO metin olarak döndürür."""
    bugun = datetime.now().date()
    return (bugun - timedelta(days=gun)).isoformat(), bugun.isoformat()


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

    if veri.get("kaynak") != "db":
        st.info("Abonelik verisine ulaşılamadı; ekran boş veriyle çiziliyor.")

    # --- 1) Üç ana metrik -------------------------------------------------
    Section(
        "Gelir Özeti",
        "Aktif aboneliklerden türetilen yinelenen gelir ve kayıp oranı.",
    ).render()

    degisim = round(seri[-1]["mrr"] - seri[-2]["mrr"], 2) if len(seri) >= 2 else None
    kolon1, kolon2, kolon3 = st.columns(3)
    with kolon1:
        st.metric(
            "MRR (Aylık Yinelenen Gelir)",
            _tl(gelir["mrr"]),
            delta=None if degisim is None else _tl(degisim),
        )
    with kolon2:
        st.metric("ARR (Yıllık Yinelenen Gelir)", _tl(gelir["arr"]))
    with kolon3:
        st.metric("Churn Oranı (90 gün)", f"{churn:.2f}%")

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
            use_container_width=True,
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

    saglik1, saglik2, saglik3 = st.columns(3)
    with saglik1:
        st.metric("🟢 Sağlıklı", dagilim["green"])
    with saglik2:
        st.metric("🟡 Uyarı", dagilim["yellow"])
    with saglik3:
        st.metric("🔴 Kritik", dagilim["red"])

    toplam_tenant = sum(dagilim.values())
    if toplam_tenant == 0:
        st.caption("Sağlık skoru hesaplanabilen tenant bulunamadı.")
    else:
        st.caption(f"Toplam {toplam_tenant} tenant değerlendirildi.")


