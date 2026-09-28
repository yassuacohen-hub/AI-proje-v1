# -*- coding: utf-8 -*-
"""P7-41: Arama ve filtreleme — tüm sekmelerde global arama.

Tüm dashboard sekmelerinde ortak arama/filtreleme:
- Global arama (firma adı, VKN, telefon, e-posta, NACE, açıklama)
- Kimlik tamlığı aralığı filtresi (ölçek tavandan türetilir, PANEL-DURUSTLUK-01)
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

from company_master import sunum  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402
from company_master.ui import bos_durum, hata_kutusu  # noqa: E402
from web_dashboard.charts import kpi_karti  # noqa: E402

log = logging.getLogger(__name__)

DB_IPUCU = "DATABASE_URL `.env` içinde doğru mu? `docker compose ps` ile servisi kontrol edin."
SONUC_SECENEKLERI: tuple[int, ...] = (50, 100, 200, 500)

# nace_source SECILIR: kodu etiketsiz gostermek D-252/4 ihlalidir. Bugun
# kodlarin %100'u tahmin; kullanici "29.10" gorup dogrulanmis saniyor.
_SECIM_SUTUNLARI = (
    "company_id, legal_name, trade_name, tax_number, company_type, "
    "status, identity_completeness, entity_confidence, primary_phone, "
    "primary_email, website_domain, nace_code, nace_source, "
    "is_ankara, is_osb_member, updated_at"
)


# ---------------------------------------------------------------------------
# Saf veri okuyucular — (veri, hata)
# ---------------------------------------------------------------------------


def _sorgu_kur(
    query: str, score_min: float, score_max: float, source: str, limit: int
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

    where.append("identity_completeness >= :score_min")
    params["score_min"] = score_min
    where.append("identity_completeness <= :score_max")
    params["score_max"] = score_max

    if source:
        where.append(
            "source_record_id IN (SELECT source_record_id FROM source_records WHERE source_name = :src)"
        )
        params["src"] = source

    params["limit"] = limit
    sql = (
        f"SELECT {_SECIM_SUTUNLARI} FROM companies WHERE {' AND '.join(where)} "
        "ORDER BY identity_completeness DESC LIMIT :limit"
    )
    return sql, params


def _satirlari_df_yap(rows: list[Any]) -> pd.DataFrame:
    """DB satırlarını DataFrame'e çevirir.

    BUG-COMPANYID-01: ``company_id`` DB'den UUID nesnesi gelir; pandas/Arrow
    bunu byte-sözlüğüne çevirdiği için DataFrame kurulmadan ÖNCE ``str()``
    ile tam UUID metnine çevrilir (kısaltma yok).

    D-249: ölçülmemiş puan 0'a çevrilmez, NaN kalır. Eski hali ``else 0``
    yazıyordu — "veri yok" ile "sıfır puan" aynı hücreye düşüyordu.

    D-252/4: ``nace_code`` etiketlenerek sunulur ("29.10 (tahmini sektör)");
    ``nace_source`` teknik kolondur, ekrana girmez.
    """
    kayitlar: list[dict[str, Any]] = []
    for r in rows:
        kayit = dict(r)
        if kayit.get("company_id") is not None:
            kayit["company_id"] = str(kayit["company_id"])
        if "nace_code" in kayit:
            kayit["nace_code"] = sunum.nace_metni(
                kayit.get("nace_code"), kayit.pop("nace_source", None)
            )
        kayitlar.append(kayit)
    df = pd.DataFrame(kayitlar)
    if "identity_completeness" in df.columns:
        df["identity_completeness"] = pd.to_numeric(
            df["identity_completeness"], errors="coerce"
        ).round(1)
    return df


def _firma_ara(
    query: str = "",
    score_min: float = 0.0,
    score_max: float = sunum.AZAMI,
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


def tamlik_bantlari(df: pd.DataFrame, tavan: float) -> dict[str, int]:
    """Tamlığı bantlara dağıtır. Bantlar tavandan türetilir (PANEL-DURUSTLUK-01).

    ``tavan`` parametre olarak alınır, içeride ``tavan_getir()`` çağrılmaz:
    fonksiyon saf kalsın ki testi DB istemesin.

    Boş girdide de anahtar kümesi dolu girdiyle aynıdır ("olculmedi" dahil);
    aksi halde grafiğin sütun sayısı veriye göre oynar.
    """
    if df is None or df.empty or "identity_completeness" not in df.columns:
        return sunum.bant_dagilimi([], tavan)
    return sunum.bant_dagilimi(df["identity_completeness"], tavan)


# ---------------------------------------------------------------------------
# Cache sarmalayıcılar
# ---------------------------------------------------------------------------


@st.cache_data(ttl=60)
def firma_ara(
    query: str = "",
    score_min: float = 0.0,
    score_max: float = sunum.AZAMI,
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
    score_min: float = 0.0,
    score_max: float = sunum.AZAMI,
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


def _ozet_kartlari(df: pd.DataFrame, tavan: float) -> None:
    """3 KPI kartı: toplam sonuç · ortalama tamlık · riskli (tek KPI dili).

    Ortalama, tavanla birlikte sunulur (D-250/7). Eski hali ``/100`` yazıyordu;
    puan 0-10 ölçeğinde olduğu için bu düpedüz yalandı.
    """
    toplam = int(len(df))
    ortalama = float(df["identity_completeness"].mean()) if toplam else 0.0
    esik = sunum.risk_esigi(tavan)
    dusuk = int((df["identity_completeness"] < esik).sum())
    kpi_karti(
        "Toplam Sonuç", toplam, ikon="🔎", kategori="musteri",
        aciklama="Filtreye uyan firma sayısı (limitle sınırlı).",
        anahtar="search-toplam",
    )
    kpi_karti(
        "Ort. Tamlık", sunum.puan_metni(ortalama, tavan), ikon="⭐", kategori="basari",
        aciklama="Sonuç kümesinin ortalama kimlik dosyası tamlığı.",
        anahtar="search-ortalama",
    )
    kpi_karti(
        "Kimlik Riski", dusuk, ikon="⚠️", kategori="uyari" if dusuk else "basari",
        aciklama=f"Tamlığı {esik:.2f} altında kalan firmalar (tavanın %30'u).",
        anahtar="search-dusuk",
    )


def _sonuclari_ciz(df: pd.DataFrame, tavan: float) -> None:
    st.success(f"✅ {len(df)} sonuç bulundu")
    col_tablo, col_kpi = st.columns([3, 1])
    with col_tablo:
        st.dataframe(df, width="stretch", hide_index=True)
    with col_kpi:
        _ozet_kartlari(df, tavan)

    st.divider()
    st.caption(f"Kimlik tamlığı dağılımı (ulaşılabilir tavan {tavan:.2f})")
    st.bar_chart(pd.Series(tamlik_bantlari(df, tavan)), width="stretch")


def render_search_tab() -> None:
    """Global arama/filtreleme alt bölümünü çizer (``admin_yonetim`` altında)."""
    st.subheader("🔍 Global Arama ve Filtreleme")

    tavan = sunum.tavan_getir()
    tam_aralik = (0.0, float(tavan))
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
        score_range = st.slider(
            f"Kimlik Tamlığı Aralığı (tavan {tavan:.2f})",
            *tam_aralik, tam_aralik, step=0.1,
            help=sunum.tavan_metni(tavan),
        )

    col_source, col_limit = st.columns(2)
    with col_source:
        source = st.selectbox("Kaynak Tipi", ["Tümü"] + kaynaklar, key="source_filter")
    with col_limit:
        limit = st.selectbox("Sonuç Sayısı", list(SONUC_SECENEKLERI), index=1, key="limit_filter")

    if not (query or tuple(score_range) != tam_aralik or source != "Tümü"):
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
            aksiyon="Arama metnini kısaltın veya tamlık aralığını genişletin.",
        )
        return
    _sonuclari_ciz(df, tavan)
