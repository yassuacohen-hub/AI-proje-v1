# -*- coding: utf-8 -*-
"""P7-31 — Admin Panel Faz 2: Veri Kalitesi Özeti sekmesi.

Kapsam:
  - company.identity_completeness aggregation (toplam/ortalama/medyan/min/max)
  - Kimlik tamlığı dağılımı — bantlar ULAŞILABILIR TAVANDAN türetilir (D-250/7)
  - Eksik alan analizi (telefon, e-posta, web, VKN, NACE, adres, parsel)
  - Kural bazlı iyileştirme önerileri
  - Kimlik riski (tavanın %30'u altı) filtreleme — riskli firma listesi + eksik alan

Kurallar:
  - st.cache_data ttl=60
  - Plotly fallback: st.bar_chart
  - kpi_karti (web_dashboard.charts) kullanımı
  - PANEL-DURUSTLUK-01: ölçek/etiket metni company_master.sunum tek kapısından gelir.
"""
from __future__ import annotations

import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master import sunum
from company_master.db.connection import get_engine
from company_master.kaynak_guvenilirlik import (
    RELIABILITY_GREEN,
    RELIABILITY_YELLOW,
    hesapla_toplu,
)
from web_dashboard.charts import kpi_karti
from web_dashboard.tabs.admin_error_handling import AdminErrorHandler

# Admin Quality logger
_admin_quality_logger = AdminErrorHandler("admin_quality")

# Analiz edilecek alanlar: kolon adı -> okunabilir etiket
# D-299: anahtarlar SQL'e ad olarak gömülür; canlı `companies` kolon adlarıyla
# birebir aynı olmak zorunda. `adres`/`osb_parsel` yazılıydı, canlıda yok
# (psycopg UndefinedColumn, HINT: companies.address). Gerçek adlar:
# `address` ve `osb_parcel`.
_QUALITY_FIELDS: dict[str, str] = {
    "primary_phone": "Telefon",
    "primary_email": "E-posta",
    "website_domain": "Web Sitesi",
    "tax_number": "VKN",
    "nace_code": "NACE",
    "address": "Adres",
    "osb_parcel": "Parsel",
}

# D-299: "dolu" gorunen ama bilgi tasimayan sablon degerler -- D-292'nin panel
# yuzeyindeki esi. 2142 kayitta `website_domain` literal 'http://www.isim.org.tr'
# (sablonun kendisi kaydedilmis, hicbiri firma adiyla ilgili degil), 523 kayitta
# OSB'nin kendi portali, 87 kayitta adres "girilmemistir" cumlesi. Bunlari dolu
# saymak "Web Sitesi %57,9" yalanini uretiyordu. Veri silinmiyor (D-8: silme
# PO'da) -- yalnizca sayarken yokluk sayiliyor.
_SABLON_DEGERLER: tuple[str, ...] = (
    "http://www.isim.org.tr",
    "https://www.ostimistihdam.com",
    "https://www.ostimonline.com/Home/OstimMain",
    "bilinmeyen@bilinmeyen.com",
    "Adres bilgisi girilmemiştir.",
)


def _dolu_kosulu(col: str) -> str:
    """Sablon degerleri yokluk sayan SQL doluluk kosulu (D-299)."""
    liste = ", ".join("'" + d.replace("'", "''") + "'" for d in _SABLON_DEGERLER)
    return f"{col} IS NOT NULL AND {col} <> '' AND {col} NOT IN ({liste})"


def _risk_esigi() -> float:
    """Risk eşiği sabit yazılmaz: tavanın oranı (D-250/7). Tavan 6.5 iken 1.95.

    Modül seviyesinde çağrılmaz — import anında DB'ye gitmek testleri ve
    DB'siz açılışı kırar.
    """
    return sunum.risk_esigi(sunum.tavan_getir())

# UI-ADMIN-ARAMA-BOSLUK-20: İçerik Boşluk Raporu (sonuçsuz arama analizi)
_BOSLUK_MIN_FREKANS = 3  # Sonuçsuz arama eşiği (modül sabiti, sihirli sayı yok)

def _terim_normalize(terim: str) -> str:
    """Arama terimini normalize et: strip + lower + çoklu boşluk tekilleştirme.

    >>> _terim_normalize("  ERP  Yazılım ")
    'erp yazılım'
    >>> _terim_normalize("erp yazılım")
    'erp yazılım'
    >>> _terim_normalize("  ERP   Yazılım  ")
    'erp yazılım'
    >>> _terim_normalize("")
    ''
    >>> _terim_normalize(None)
    ''
    """
    if not terim:
        return ""
    # strip + lower + çoklu boşluğu tek boşluğa indir
    return " ".join(terim.strip().lower().split())

# PO-BACK-11: sources + source_records üzerinden kaynak bazlı çekiş istatistiği
_SOURCE_RELIABILITY_SQL = """
    SELECT s.source_id, s.source_name,
           COUNT(sr.source_record_id) AS toplam_cekis,
           SUM(CASE WHEN sr.raw_payload IS NOT NULL THEN 1 ELSE 0 END) AS basarili_cekis,
           MAX(sr.collected_at) AS son_cekis_zaman
    FROM sources s
    LEFT JOIN source_records sr ON sr.source_id = s.source_id
    GROUP BY s.source_id, s.source_name
    ORDER BY s.source_name
"""


# ---------------------------------------------------------------------------
# Veri Yükleme Fonksiyonları
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def load_quality_overview() -> dict[str, Any]:
    """Genel kalite skoru özeti: toplam, ortalama, medyan, min, max, riskli oran."""
    result: dict[str, Any] = {
        "toplam_firma": 0,
        "ortalama_skor": 0.0,
        "medyan_skor": 0.0,
        "min_skor": 0.0,
        "max_skor": 0.0,
        "riskli_sayisi": 0,
        "riskli_orani": 0.0,
    }
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT COUNT(*) as toplam, AVG(identity_completeness) as ort, "
                "MIN(identity_completeness) as min_s, MAX(identity_completeness) as max_s, "
                "SUM(CASE WHEN identity_completeness < :esik THEN 1 ELSE 0 END) as riskli "
                "FROM companies WHERE is_ankara=TRUE AND is_osb_member=TRUE"
            ), {"esik": _risk_esigi()}).mappings().first()
            if row and row["toplam"]:
                result["toplam_firma"] = row["toplam"]
                result["ortalama_skor"] = round(float(row["ort"] or 0), 1)
                result["min_skor"] = round(float(row["min_s"] or 0), 1)
                result["max_skor"] = round(float(row["max_s"] or 0), 1)
                result["riskli_sayisi"] = row["riskli"] or 0
                result["riskli_orani"] = round(
                    result["riskli_sayisi"] / max(result["toplam_firma"], 1) * 100, 1
                )

            # Medyan: cross-DB uyumluluk için Python tarafında hesapla
            scores = conn.execute(text(
                "SELECT identity_completeness FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE "
                "AND identity_completeness IS NOT NULL"
            )).scalars().all()
            if scores:
                scores_f = [float(s) for s in scores]
                result["medyan_skor"] = round(statistics.median(scores_f), 1)
    except Exception as exc:
        _admin_quality_logger.warning("Kalite özeti yüklenemedi", exc)
    return result


@st.cache_data(ttl=60)
def load_score_distribution() -> pd.DataFrame:
    """Kimlik tamlığı dağılımı. Bantlar SQL'de sabit değil, tavandan türetilir.

    Eski hali 80-100/60-79 gibi 0-100 eşikleri kullanıyordu; puan azami 6.50
    olduğu için tüm firmalar tek kovaya yığılıyordu (PANEL-DURUSTLUK-01).
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            puanlar = conn.execute(text(
                "SELECT identity_completeness FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE"
            )).scalars().all()
        if puanlar:
            tavan = sunum.tavan_getir()
            sayac = sunum.bant_dagilimi(puanlar, tavan)
            sira = [e for e, _a, _u in sunum.bantlar(tavan)] + ["olculmedi"]
            df = pd.DataFrame(
                [{"bucket": k, "adet": sayac[k]} for k in sira if sayac.get(k)]
            )
            if not df.empty:
                df["bucket"] = pd.Categorical(df["bucket"], categories=sira, ordered=True)
                return df.sort_values("bucket").reset_index(drop=True)
    except Exception as exc:
        _admin_quality_logger.warning("Skor dağılımı yüklenemedi", exc)
    return pd.DataFrame(columns=["bucket", "adet"])


_FRESHNESS_KOVALARI = ("0-7g", "8-30g", "31-90g", "90g+")


@st.cache_data(ttl=60)
def load_freshness_distribution() -> pd.DataFrame:
    """UI-ADMIN-GUNCELLIK-KOVA-10 (SSOT §9 K3): updated_at yaşına göre kova dağılımı.

    Yaş hesabı Python tarafında yapılır (load_quality_overview() medyan
    hesaplamasındaki kalıpla aynı gerekçe: cross-DB uyumluluk).
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT updated_at FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE AND updated_at IS NOT NULL"
            )).scalars().all()
        if rows:
            simdi = datetime.now()
            sayac = dict.fromkeys(_FRESHNESS_KOVALARI, 0)
            for deger in rows:
                try:
                    gun = (simdi - datetime.fromisoformat(str(deger)[:19])).days
                except (ValueError, TypeError):
                    continue
                if gun <= 7:
                    sayac["0-7g"] += 1
                elif gun <= 30:
                    sayac["8-30g"] += 1
                elif gun <= 90:
                    sayac["31-90g"] += 1
                else:
                    sayac["90g+"] += 1
            return pd.DataFrame({
                "kova": list(_FRESHNESS_KOVALARI),
                "adet": [sayac[k] for k in _FRESHNESS_KOVALARI],
            })
    except Exception as exc:
        _admin_quality_logger.warning("Güncellik dağılımı yüklenemedi", exc)
    return pd.DataFrame(columns=["kova", "adet"])


@st.cache_data(ttl=60)
def load_missing_field_analysis() -> pd.DataFrame:
    """Eksik alan analizi: her alanın eksiklik oranı (doluluk analizinin tersi)."""
    result: list[dict[str, Any]] = []
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT COUNT(*) as total FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE"
            )).mappings().first()
            total = (row["total"] or 1) if row else 1

            for col, label in _QUALITY_FIELDS.items():
                try:
                    cnt_row = conn.execute(text(
                        f"SELECT COUNT(*) as cnt FROM companies "
                        f"WHERE is_ankara=TRUE AND is_osb_member=TRUE "
                        f"AND NOT ({_dolu_kosulu(col)})"
                    )).mappings().first()
                    eksik = cnt_row["cnt"] if cnt_row else 0
                except Exception as exc:
                    # D-249/D-299: ölçülemeyen alan 0 taşımaz. `eksik = 0`
                    # panelde "%0 eksik" yalanı üretiyordu — kolon adı yanlışken
                    # kullanıcı alanı tam sanıyordu. Ölçülemeyen satır çizilmez.
                    # Rollback şart: tek hatalı alan transaction'ı abort edince
                    # arkasındaki tüm alanlar da InFailedSqlTransaction ile düşüyordu.
                    conn.rollback()
                    _admin_quality_logger.warning(f"Alan {label} eksik sayımı başarısız", exc)
                    continue
                result.append({
                    "Alan": label,
                    "Eksik": eksik,
                    "Toplam": total,
                    "Eksiklik (%)": round(eksik / max(total, 1) * 100, 1),
                })
    except Exception as exc:
        # D-249: olculmemis tablo "hepsi %0 eksik" diye sunulamaz; bos birakilir.
        _admin_quality_logger.warning("Eksik alan analizi yüklenemedi", exc)
    return pd.DataFrame(result)


@st.cache_data(ttl=60)
def load_risky_companies(limit: int = 100) -> pd.DataFrame:
    """Kimlik riski (tamlık < risk eşiği) firmaları — eksik alan özetiyle."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT company_id, legal_name, trade_name, identity_completeness,
                       CASE WHEN primary_phone IS NULL OR primary_phone='' THEN 1 ELSE 0 END as e_tel,
                       CASE WHEN primary_email IS NULL OR primary_email='' THEN 1 ELSE 0 END as e_email,
                       CASE WHEN website_domain IS NULL OR website_domain='' THEN 1 ELSE 0 END as e_web,
                       CASE WHEN tax_number IS NULL OR tax_number='' THEN 1 ELSE 0 END as e_vkn,
                       CASE WHEN nace_code IS NULL OR nace_code='' THEN 1 ELSE 0 END as e_nace,
                       CASE WHEN address IS NULL OR address='' THEN 1 ELSE 0 END as e_adres
                FROM companies
                WHERE is_ankara=TRUE AND is_osb_member=TRUE
                  AND identity_completeness < :esik
                ORDER BY identity_completeness ASC
                LIMIT :limit
            """), {"esik": _risk_esigi(), "limit": limit}).mappings().all()
            if rows:
                df = pd.DataFrame([dict(r) for r in rows])

                def _eksik_ozet(r: pd.Series) -> str:
                    eksikler = []
                    if r["e_tel"]:
                        eksikler.append("Tel")
                    if r["e_email"]:
                        eksikler.append("Email")
                    if r["e_web"]:
                        eksikler.append("Web")
                    if r["e_vkn"]:
                        eksikler.append("VKN")
                    if r["e_nace"]:
                        eksikler.append("NACE")
                    if r["e_adres"]:
                        eksikler.append("Adres")
                    return ", ".join(eksikler) if eksikler else "-"

                df["Eksik Alanlar"] = df.apply(_eksik_ozet, axis=1)
                df = df.drop(columns=["e_tel", "e_email", "e_web", "e_vkn", "e_nace", "e_adres"])
                df["identity_completeness"] = df["identity_completeness"].apply(
                    lambda x: round(float(x), 1) if x is not None else 0
                )
                df = df.rename(columns={
                    "company_id": "Firma ID", "legal_name": "Unvan",
                    "trade_name": "Ticari Ad",
                    "identity_completeness": "Kimlik Tamlığı",
                })
                return df
    except Exception as exc:
        _admin_quality_logger.warning("Riskli firmalar yüklenemedi", exc)
    return pd.DataFrame(
        columns=["Firma ID", "Unvan", "Ticari Ad", "Kimlik Tamlığı", "Eksik Alanlar"]
    )


@st.cache_data(ttl=60)
def load_icerik_bosluk() -> pd.DataFrame:
    """UI-ADMIN-ARAMA-BOSLUK-20: İçerik Boşluk Raporu — Sonuçsuz arama frekans analizi.

    user_activity_log tablosundan olay_tipi='arama' AND basarili=FALSE olan kayıtları
    son 30 günde çeker, terimleri normalize edip frekans sayar, eşik >=3 uygular.

    Returns:
        pd.DataFrame: terim, frekans, ilk_gorulme, son_gorulme kolonları.
        Tablo/veri yoksa boş DataFrame döner (rozet kontrolü üst katmanda).
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Tablo var mı kontrolü
            if not _db_yardim.tablo_var_mi(conn, "user_activity_log"):
                return pd.DataFrame(columns=["terim", "frekans", "ilk_gorulme", "son_gorulme"])

            rows = conn.execute(text("""
                SELECT
                    detay->>'terim' as ham_terim,
                    olay_zamani::date as olay_tarih
                FROM user_activity_log
                WHERE olay_tipi = 'arama'
                  AND basarili = FALSE
                  AND olay_zamani >= (CURRENT_DATE - INTERVAL '30 days')
                  AND detay IS NOT NULL
                  AND detay->>'terim' IS NOT NULL
            """)).mappings().all()

            if not rows:
                return pd.DataFrame(columns=["terim", "frekans", "ilk_gorulme", "son_gorulme"])

            # DataFrame'e çevir ve normalize et
            df = pd.DataFrame([dict(r) for r in rows])
            df["terim"] = df["ham_terim"].apply(_terim_normalize)

            # Boş normalize edilmiş terimleri at
            df = df[df["terim"] != ""]

            if df.empty:
                return pd.DataFrame(columns=["terim", "frekans", "ilk_gorulme", "son_gorulme"])

            # Grupla ve say
            grouped = df.groupby("terim").agg(
                frekans=("ham_terim", "count"),
                ilk_gorulme=("olay_tarih", "min"),
                son_gorulme=("olay_tarih", "max"),
            ).reset_index()

            # Eşik uygula
            grouped = grouped[grouped["frekans"] >= _BOSLUK_MIN_FREKANS]

            if grouped.empty:
                return pd.DataFrame(columns=["terim", "frekans", "ilk_gorulme", "son_gorulme"])

            # Sırala: frekans azalan
            grouped = grouped.sort_values("frekans", ascending=False)

            # Tarih formatı
            grouped["ilk_gorulme"] = grouped["ilk_gorulme"].apply(lambda x: x.strftime("%Y-%m-%d"))
            grouped["son_gorulme"] = grouped["son_gorulme"].apply(lambda x: x.strftime("%Y-%m-%d"))

            return grouped[["terim", "frekans", "ilk_gorulme", "son_gorulme"]]

    except Exception as exc:
        _admin_quality_logger.warning("İçerik boşluk raporu yüklenemedi", exc)
        return pd.DataFrame(columns=["terim", "frekans", "ilk_gorulme", "son_gorulme"])


def generate_improvement_suggestions(
    missing_df: pd.DataFrame, overview: dict[str, Any]
) -> list[dict[str, str]]:
    """Eksik alan oranlarına ve genel risk oranına göre kural bazlı iyileştirme önerileri üretir."""
    suggestions: list[dict[str, str]] = []
    if not missing_df.empty:
        for _, row in missing_df.sort_values("Eksiklik (%)", ascending=False).iterrows():
            oran = row["Eksiklik (%)"]
            if oran >= 50:
                oncelik = "🔴 Yüksek"
            elif oran >= 25:
                oncelik = "🟠 Orta"
            elif oran >= 10:
                oncelik = "🟡 Düşük"
            else:
                continue
            suggestions.append({
                "Öncelik": oncelik,
                "Alan": row["Alan"],
                "Eksiklik (%)": f"%{oran}",
                "Öneri": f"{row['Alan']} alanı firmaların %{oran}'inde eksik — "
                         f"zenginleştirme/scraping kaynağı önceliklendirilmeli.",
            })

    riskli_oran = overview.get("riskli_orani", 0)
    if riskli_oran >= 10:
        suggestions.insert(0, {
            "Öncelik": "🔴 Yüksek",
            "Alan": "Genel Kalite",
            "Eksiklik (%)": f"%{riskli_oran}",
            "Öneri": f"Firmaların %{riskli_oran}'i risk eşiğinin "
                     f"(tamlık<{_risk_esigi():.2f}) altında — "
                     f"toplu yeniden zenginleştirme (recalc + scrape) planlanmalı.",
        })
    return suggestions


# ---------------------------------------------------------------------------
# Grafik Fonksiyonları
# ---------------------------------------------------------------------------

def _chart_distribution(dist_df: pd.DataFrame) -> None:
    if dist_df.empty:
        st.info("Skor dağılımı verisi bulunamadı.")
        return
    try:
        import plotly.express as px
        fig = px.bar(
            dist_df, x="bucket", y="adet",
            title="Kalite Skoru Dağılımı (Bucket Bazlı)",
            labels={"bucket": "Skor Aralığı", "adet": "Firma Sayısı"},
            color="adet", color_continuous_scale="RdYlGn",
        )
        fig.update_layout(height=320, margin=dict(t=40, b=20))
        st.plotly_chart(fig, width="stretch")
    except ImportError:
        st.bar_chart(dist_df.set_index("bucket")["adet"], width="stretch")


def _chart_freshness(fresh_df: pd.DataFrame) -> None:
    """UI-ADMIN-GUNCELLIK-KOVA-10: updated_at yaş kovası grafiği."""
    if fresh_df.empty:
        st.info("Güncellik verisi bulunamadı.")
        return
    try:
        import plotly.express as px
        fig = px.bar(
            fresh_df, x="kova", y="adet",
            title="Veri Güncellik Dağılımı (updated_at Yaşı)",
            labels={"kova": "Yaş Aralığı", "adet": "Firma Sayısı"},
            color="adet", color_continuous_scale="Blues",
        )
        fig.update_layout(height=300, margin=dict(t=40, b=20))
        st.plotly_chart(fig, width="stretch")
    except ImportError:
        st.bar_chart(fresh_df.set_index("kova")["adet"], width="stretch")


def _chart_missing_fields(missing_df: pd.DataFrame) -> None:
    if missing_df.empty:
        st.info("Eksik alan verisi bulunamadı.")
        return
    col_table, col_chart = st.columns([1, 1])
    with col_table:
        st.dataframe(missing_df, width="stretch", hide_index=True)
    with col_chart:
        try:
            import plotly.express as px
            fig = px.bar(
                missing_df, x="Alan", y="Eksiklik (%)",
                title="Alan Bazlı Eksiklik Oranları (%)",
                color="Eksiklik (%)", color_continuous_scale="Reds",
            )
            fig.update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(fig, width="stretch")
        except ImportError:
            st.bar_chart(missing_df.set_index("Alan")["Eksiklik (%)"], width="stretch")


# ---------------------------------------------------------------------------
# Render Fonksiyonu
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def load_source_reliability() -> list[dict[str, Any]]:
    """PO-BACK-11: Kaynak bazlı güvenilirlik skorları (DB yoksa boş liste)."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text(_SOURCE_RELIABILITY_SQL)).mappings().all()
        ham = [
            {
                "kaynak_id": str(r["source_id"]),
                "kaynak_adi": r["source_name"] or "",
                "toplam_cekis": int(r["toplam_cekis"] or 0),
                "basarili_cekis": int(r["basarili_cekis"] or 0),
                "son_cekis_zaman": (
                    r["son_cekis_zaman"].isoformat()
                    if isinstance(r["son_cekis_zaman"], datetime)
                    else (str(r["son_cekis_zaman"]) if r["son_cekis_zaman"] else None)
                ),
            }
            for r in rows
        ]
        return [k.to_dict() for k in hesapla_toplu(ham)]
    except Exception as exc:
        _admin_quality_logger.warning("Kaynak güvenilirlik yüklenemedi", exc)
        return []


def _render_icerik_bosluk() -> None:
    """UI-ADMIN-ARAMA-BOSLUK-20: İçerik Boşluk Raporu — Sonuçsuz arama frekans analizi."""
    st.subheader("🔍 İçerik Boşluk Raporu (Sonuçsuz Aramalar)")
    st.caption(
        "Son 30 günde sonuç vermeyen aramalar (basarili=FALSE). "
        f"Terimler normalize edilip (strip+lower+boşluk tekilleştirme) "
        f"frekansa göre gruplandırıldı. Eşik: >= {_BOSLUK_MIN_FREKANS} tekrar."
    )

    bosluk_df = load_icerik_bosluk()

    # _db_yardim.tablo_var_mi pattern: tablo/veri yoksa rozet göster
    if bosluk_df.empty:
        st.warning("⚠️ Veri kaynağı yok — user_activity_log tablosu bulunamadı veya sonuçsuz arama kaydı yok.")
        return

    # Metrik kartları
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📋 Farklı Terim Sayısı", len(bosluk_df))
    with c2:
        st.metric("🔁 Toplam Sonuçsuz Arama", int(bosluk_df["frekans"].sum()))
    with c3:
        st.metric("📊 Eşik", f">= {_BOSLUK_MIN_FREKANS}")

    # Tablo
    display_df = bosluk_df.rename(columns={
        "terim": "Arama Terimi",
        "frekans": "Frekans",
        "ilk_gorulme": "İlk Görülme",
        "son_gorulme": "Son Görülme",
    })
    st.dataframe(display_df, width="stretch", hide_index=True)

    # İndirme butonu
    csv = bosluk_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 CSV İndir",
        data=csv,
        file_name=f"icerik_bosluk_raporu_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="icerik_bosluk_download",
    )


def _render_kaynak_guvenilirlik() -> None:
    """PO-BACK-11: Kaynak tablosu + eşik altı uyarı kartı."""
    kaynaklar = load_source_reliability()
    if not kaynaklar:
        st.info("Kaynak çekiş verisi bulunamadı (sources/source_records boş veya DB erişilemiyor).")
        return

    kirmizi = [k for k in kaynaklar if k["skor"] < RELIABILITY_YELLOW]
    sari = [k for k in kaynaklar if RELIABILITY_YELLOW <= k["skor"] < RELIABILITY_GREEN]

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Kaynak", len(kaynaklar))
    c2.metric(f"Sarı Bant (<{RELIABILITY_GREEN:.0f})", len(sari))
    c3.metric(f"Kırmızı Bant (<{RELIABILITY_YELLOW:.0f})", len(kirmizi))

    if kirmizi:
        st.error(
            "🔴 Eşik altı kaynaklar: "
            + ", ".join(f"{k['kaynak_adi']} ({k['skor']:.0f})" for k in kirmizi)
        )
    elif sari:
        st.warning(
            "🟡 Dikkat gerektiren kaynaklar: "
            + ", ".join(f"{k['kaynak_adi']} ({k['skor']:.0f})" for k in sari)
        )
    else:
        st.success("Tüm kaynaklar yeşil bantta.")

    df = pd.DataFrame(kaynaklar)[
        ["kaynak_adi", "skor", "band", "tazelik_skoru", "hata_orani",
         "tutarlilik_skoru", "toplam_cekis", "basarili_cekis", "son_cekis_zaman"]
    ].rename(columns={
        "kaynak_adi": "Kaynak", "skor": "Skor", "band": "Bant",
        "tazelik_skoru": "Tazelik", "hata_orani": "Hata Oranı",
        "tutarlilik_skoru": "Tutarlılık", "toplam_cekis": "Toplam Çekiş",
        "basarili_cekis": "Başarılı Çekiş", "son_cekis_zaman": "Son Çekiş",
    }).sort_values("Skor")
    st.dataframe(df, width="stretch", hide_index=True)


def render_quality_tab() -> None:
    """P7-31: Admin Panel Faz 2 — Kimlik Dosyası Tamlığı sekmesi."""

    st.subheader("🧪 Kimlik Dosyası Tamlığı")
    st.caption(
        "Tamlık dağılımı, eksik alan analizi, iyileştirme önerileri — "
        "Son güncelleme: " + datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    if st.button("🔄 Yenile", key="admin-quality-refresh"):
        st.cache_data.clear()
        st.rerun()

    # D-250/7: puan tek başına gösterilmez; tavan ve kilitli alanlar ilan edilir.
    ozet = sunum.tavan_ozeti()
    tavan = ozet["tavan"]
    st.info(ozet["metin"])
    with st.expander("Kilitli alanlar — puan niçin bu tavanda duruyor"):
        st.dataframe(
            pd.DataFrame(ozet["kilit_satirlari"]).rename(columns={
                "alan": "Alan", "kayip_puan": "Kayıp Puan", "gerekce": "Gerekçe",
            }),
            width="stretch", hide_index=True,
        )

    overview = load_quality_overview()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_karti("📦 Toplam Firma", f"{overview['toplam_firma']:,}", kategori="kalite")
    with c2:
        kpi_karti(
            "📊 Ortalama Tamlık",
            sunum.puan_metni(overview["ortalama_skor"], tavan),
            kategori="kalite",
        )
    with c3:
        kpi_karti(
            "📐 Medyan Tamlık",
            sunum.puan_metni(overview["medyan_skor"], tavan),
            kategori="kalite",
        )
    with c4:
        kpi_karti(
            f"⚠️ Riskli Firma (< {sunum.risk_esigi(tavan):.2f})",
            f"{overview['riskli_sayisi']:,}",
            delta=f"%{overview['riskli_orani']} oranında" if overview["riskli_sayisi"] else None,
            kategori="kalite",
        )

    st.divider()
    st.subheader("📈 Kimlik Tamlığı Dağılımı")
    dist_df = load_score_distribution()
    _chart_distribution(dist_df)

    st.divider()
    st.subheader("📅 Veri Güncellik")
    fresh_df = load_freshness_distribution()
    _chart_freshness(fresh_df)

    st.divider()
    st.subheader("🔍 Eksik Alan Analizi")
    missing_df = load_missing_field_analysis()
    _chart_missing_fields(missing_df)

    st.divider()
    st.subheader("💡 İyileştirme Önerileri")
    suggestions = generate_improvement_suggestions(missing_df, overview)
    if suggestions:
        st.dataframe(pd.DataFrame(suggestions), width="stretch", hide_index=True)
    else:
        st.success("Kritik eksiklik tespit edilmedi — veri kalitesi genel olarak iyi durumda.")

    st.divider()
    st.subheader("🛰️ Kaynak Güvenilirliği")
    _render_kaynak_guvenilirlik()

    st.divider()
    _render_icerik_bosluk()

    st.divider()
    esik = sunum.risk_esigi(tavan)
    st.subheader(f"🚨 Kimlik Riski Filtreleme (tamlık < {esik:.2f})")
    limit = st.slider(
        "Gösterilecek maksimum firma sayısı",
        min_value=10, max_value=500, value=100, step=10,
        key="quality_risk_limit",
    )
    risky_df = load_risky_companies(limit=limit)
    if risky_df.empty:
        st.success(f"Tamlık < {esik:.2f} aralığında firma bulunamadı — risk yok.")
    else:
        st.caption(f"{len(risky_df)} firma listeleniyor (limit: {limit})")
        st.dataframe(risky_df, width="stretch", hide_index=True)
