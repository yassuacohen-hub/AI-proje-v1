# -*- coding: utf-8 -*-
"""P7-41: Arama ve filtreleme — tüm sekmelerde global arama.

Tüm dashboard sekmelerinde ortak arama/filtreleme:
- Global arama (firma adı, VKN, telefon, e-posta, NACE, açıklama)
- Kalite skoru aralığı filtresi
- Kaynak tipi filtresi
- Sonuç sayısı gösterimi

ADMIN-SEARCH-01 (roo): admin sekme kalıbına geçiş.
- Veri okuyucular saf ``(veri, hata)`` sözleşmesi döndürür; ``st.warning``
  cache içinden çıkarıldı, hata ``logging`` ile kayda geçer.
- 3 × ``st.metric`` → ``kpi_karti``; hata → ``hata_kutusu``; boş → ``bos_durum``.
- ``search_companies`` / ``get_source_names`` geriye dönük uyumluluk için
  korunur (``admin_musteriler`` bunları kullanır).
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine  # noqa: E402
from company_master.ui import bos_durum, hata_kutusu  # noqa: E402
from web_dashboard.charts import kpi_karti  # noqa: E402

log = logging.getLogger(__name__)

DB_IPUCU = "DATABASE_URL `.env` içinde doğru mu? `docker compose ps` ile servisi kontrol edin."
DUSUK_KALITE_ESIK = 30
SONUC_SECENEKLERI: tuple[int, ...] = (50, 100, 200, 500)
KALITE_BANTLARI: tuple[tuple[str, int, int], ...] = (
    ("80-100 (Yüksek)", 80, 101),
    ("60-79 (İyi)", 60, 80),
    ("40-59 (Orta)", 40, 60),
    ("20-39 (Düşük)", 20, 40),
    ("0-19 (Çok Düşük)", 0, 20),
)

_SECIM_SUTUNLARI = (
    "company_id, legal_name, trade_name, tax_number, company_type, "
    "status, data_quality_score, entity_confidence, primary_phone, "
    "primary_email, website_domain, nace_code, is_ankara, is_osb_member, updated_at"
)


# ---------------------------------------------------------------------------
# Saf veri okuyucular — (veri, hata)
# ---------------------------------------------------------------------------


def _sorgu_kur(
    query: str, score_min: int, score_max: int, source: str, limit: int
) -> tuple[str, dict[str, Any]]:
    """Filtrelerden parametreli SQL üretir → ``(sql, params)``."""
    where: list[str] = []
    params: dict[str, Any] = {}

    if query:
        where.append(
            "(legal_name ILIKE :q OR tax_number ILIKE :q OR primary_email ILIKE :q "
            "OR primary_phone ILIKE :q OR description ILIKE :q OR nace_code ILIKE :q)"
        )
        params["q"] = f"%{query}%"

    where.append("data_quality_score >= :score_min")
    params["score_min"] = score_min
    where.append("data_quality_score <= :score_max")
    params["score_max"] = score_max

    if source:
        where.append(
            "source_record_id IN (SELECT source_record_id FROM source_records WHERE source_name = :src)"
        )
        params["src"] = source

    params["limit"] = limit
    sql = (
        f"SELECT {_SECIM_SUTUNLARI} FROM companies WHERE {' AND '.join(where)} "
        "ORDER BY data_quality_score DESC LIMIT :limit"
    )
    return sql, params


def _satirlari_df_yap(rows: list[Any]) -> pd.DataFrame:
    """DB satırlarını DataFrame'e çevirir.

    BUG-COMPANYID-01: ``company_id`` DB'den UUID nesnesi gelir; pandas/Arrow
    bunu byte-sözlüğüne çevirdiği için DataFrame kurulmadan ÖNCE ``str()``
    ile tam UUID metnine çevrilir (kısaltma yok).
    """
    kayitlar: list[dict[str, Any]] = []
    for r in rows:
        kayit = dict(r)
        if kayit.get("company_id") is not None:
            kayit["company_id"] = str(kayit["company_id"])
        kayitlar.append(kayit)
    df = pd.DataFrame(kayitlar)
    if "data_quality_score" in df.columns:
        df["data_quality_score"] = df["data_quality_score"].apply(
            lambda x: round(float(x), 1) if x is not None else 0
        )
    return df


def _firma_ara(
    query: str = "",
    score_min: int = 0,
    score_max: int = 100,
    source: str = "",
    limit: int = 100,
) -> tuple[pd.DataFrame | None, str | None]:
    """Global arama → ``(df, hata)``. Satır yoksa boş DataFrame, hata varsa ``None``."""
    sql, params = _sorgu_kur(query, score_min, score_max, source, limit)
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return _satirlari_df_yap(list(rows)), None
    except Exception as exc:  # noqa: BLE001
        log.warning("admin_search: firma arama başarısız: %s", exc)
        return None, f"{type(exc).__name__}: {exc}"


def _kaynak_adlari() -> tuple[list[str], str | None]:
    """``sources`` tablosundaki kaynak adları → ``(liste, hata)``."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT source_name FROM sources ORDER BY source_name")
            ).mappings().all()
        return [r["source_name"] for r in rows], None
    except Exception as exc:  # noqa: BLE001
        log.warning("admin_search: kaynak listesi okunamadı: %s", exc)
        return [], f"{type(exc).__name__}: {exc}"


def kalite_bantlari(df: pd.DataFrame) -> dict[str, int]:
    """Kalite skorunu 5 banda dağıtır (grafik ve test için saf)."""
    if df is None or df.empty or "data_quality_score" not in df.columns:
        return {ad: 0 for ad, _, _ in KALITE_BANTLARI}
    skor = df["data_quality_score"]
    return {ad: int(((skor >= alt) & (skor < ust)).sum()) for ad, alt, ust in KALITE_BANTLARI}


# ---------------------------------------------------------------------------
# Cache sarmalayıcılar
# ---------------------------------------------------------------------------


@st.cache_data(ttl=60)
def firma_ara(
    query: str = "",
    score_min: int = 0,
    score_max: int = 100,
    source: str = "",
    limit: int = 100,
) -> tuple[pd.DataFrame | None, str | None]:
    """``_firma_ara`` cache sarmalayıcısı (60 sn)."""
    return _firma_ara(query, score_min, score_max, source, limit)


@st.cache_data(ttl=300)
def kaynak_adlari() -> tuple[list[str], str | None]:
    """``_kaynak_adlari`` cache sarmalayıcısı (5 dk)."""
    return _kaynak_adlari()


def search_companies(
    query: str = "",
    score_min: int = 0,
    score_max: int = 100,
    source: str = "",
    limit: int = 100,
) -> pd.DataFrame | None:
    """Geriye dönük uyumluluk: yalnız DataFrame döndürür (hata loglanır)."""
    df, _hata = firma_ara(query, score_min, score_max, source, limit)
    return df


def get_source_names() -> list[str]:
    """Geriye dönük uyumluluk: yalnız kaynak listesi döndürür (hata loglanır)."""
    kaynaklar, _hata = kaynak_adlari()
    return kaynaklar


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def _ozet_kartlari(df: pd.DataFrame) -> None:
    """3 KPI kartı: toplam sonuç · ortalama kalite · düşük kalite (tek KPI dili)."""
    toplam = int(len(df))
    ortalama = float(df["data_quality_score"].mean()) if toplam else 0.0
    dusuk = int((df["data_quality_score"] < DUSUK_KALITE_ESIK).sum())
    kpi_karti(
        "Toplam Sonuç", toplam, ikon="🔎", kategori="musteri",
        aciklama="Filtreye uyan firma sayısı (limitle sınırlı).",
        anahtar="search-toplam",
    )
    kpi_karti(
        "Ort. Kalite", ortalama, ondalik=1, birim="/100", ikon="⭐", kategori="basari",
        aciklama="Sonuç kümesinin ortalama veri kalitesi.",
        anahtar="search-ortalama",
    )
    kpi_karti(
        "Düşük Kalite", dusuk, ikon="⚠️", kategori="uyari" if dusuk else "basari",
        aciklama=f"Skoru {DUSUK_KALITE_ESIK} altında kalan firmalar.",
        anahtar="search-dusuk",
    )


def _sonuclari_ciz(df: pd.DataFrame) -> None:
    st.success(f"✅ {len(df)} sonuç bulundu")
    col_tablo, col_kpi = st.columns([3, 1])
    with col_tablo:
        st.dataframe(df, width="stretch", hide_index=True)
    with col_kpi:
        _ozet_kartlari(df)

    st.divider()
    st.caption("Kalite skoru dağılımı")
    st.bar_chart(pd.Series(kalite_bantlari(df)), width="stretch")


def render_search_tab() -> None:
    """Global arama/filtreleme alt bölümünü çizer (``admin_yonetim`` altında)."""
    st.subheader("🔍 Global Arama ve Filtreleme")

    kaynaklar, kaynak_hatasi = kaynak_adlari()
    if kaynak_hatasi:
        hata_kutusu("Kaynak listesi okunamadı", kaynak_hatasi, DB_IPUCU)

    col_search, col_filter = st.columns([3, 2])
    with col_search:
        query = st.text_input(
            "🔍 Firma Ara",
            placeholder="Firma adı, VKN, telefon, e-posta, NACE, açıklama...",
            key="global_search",
        )
    with col_filter:
        score_range = st.slider("Kalite Skoru Aralığı", 0, 100, (0, 100))

    col_source, col_limit = st.columns(2)
    with col_source:
        source = st.selectbox("Kaynak Tipi", ["Tümü"] + kaynaklar, key="source_filter")
    with col_limit:
        limit = st.selectbox("Sonuç Sayısı", list(SONUC_SECENEKLERI), index=1, key="limit_filter")

    if not (query or score_range != (0, 100) or source != "Tümü"):
        st.info("🔍 Arama yapın veya filtre seçin; sonuçlar burada listelenir.")
        return

    df, hata = firma_ara(
        query=query,
        score_min=score_range[0],
        score_max=score_range[1],
        source=source if source != "Tümü" else "",
        limit=limit,
    )
    if hata:
        hata_kutusu("Arama sorgusu çalıştırılamadı", hata, DB_IPUCU)
        return
    if df is None or df.empty:
        bos_durum(
            "Bu filtrelerle eşleşen firma yok.",
            ikon="🔍",
            aksiyon="Arama metnini kısaltın veya kalite aralığını genişletin.",
        )
        return
    _sonuclari_ciz(df)
