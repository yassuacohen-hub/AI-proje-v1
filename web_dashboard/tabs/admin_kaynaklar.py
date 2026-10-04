# -*- coding: utf-8 -*-
"""UI-ADMIN-KAYNAKLAR-SAYFA-34: "Veri Kaynakları" ekranı — 0050 kazıma tablolarının okuyucusu.

Kapsam:
  - ``scrape_audit_log``  → kaynak başına toplam/başarılı çekiş, son çalışma zamanı
  - ``scrape_errors``     → son 20 hata
  - ``scrape_pages``      → kaynak (domain) başına toplanan sayfa adedi

ADMIN-UI-10 kalıbı (PageHeader -> SectionNav -> Section) `admin_musteriler.py`'den
alındı; renk/ikon/tipografi değişmedi.

Kurallar:
  - Yazma yok. 0050 tablolarının tek yazıcısı `etl/scrape_kayit.py::KazimaYazici` kalır.
    (Crawl Kontrolü yalnız `st.session_state` günceller ve log yazar; tabloya yazmaz.)
  - UI-ADMIN-CRAWL-TASI-35: Crawl Kontrolü bloğu `webhook_monitor.py`'den buraya
    **taşındı**; sabitler ve `_crawl_is_enabled` / `_log_crawl_action` tek tanımlıdır.
  - Ölçüm canlı veritabanından okunur (D-238); uydurma sayı yazılmaz.
  - "Veri yok" ile "0" ayrıdır (D-249): kayıt yoksa rozet "Henüz kazıma yapılmadı" der.
  - Her blok veri kaynağını `st.caption` ile söyler (D-213 VERI-ETIKET-01).
  - `st.metric` kullanılmaz; kartlar `charts.kpi_karti` ile çizilir (ADMIN-KPI-KART-02).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master import kaynak_guvenilirlik  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402
from company_master.ui import PageHeader, Section, SectionNav  # noqa: E402
from web_dashboard.charts import kpi_karti  # noqa: E402  (UI-CHART-01)
from web_dashboard.tabs._db_yardim import tablo_var_mi  # noqa: E402

#: ADMIN-UI-10 — Bölümler tek yerde tanımlanır (anchor tutarlılığı).
BOLUMLER: tuple[Section, ...] = (
    Section("Durum Özeti", "Her kaynağın toplam çekişi, başarı oranı ve sağlık rozeti.",
            ikon="📡", kimlik="durum-ozeti"),
    Section("Son Çalışmalar", "En son kazıma denemeleri ve süre/byte ölçümleri.",
            ikon="🧾", kimlik="son-calismalar"),
    Section("Hatalar", "Son 20 kazıma hatası; yeniden deneme ve fallback durumu.",
            ikon="⚠️", kimlik="hatalar"),
    Section("Toplanan Sayfalar", "Kaynak başına toplanan sayfa adedi ve ham veri hacmi.",
            ikon="📄", kimlik="toplanan-sayfalar"),
)

GIRIS_METNI = (
    "OSINT kazıma kaynaklarının durumunu tek ekrandan izleyin: hangi kaynak ne zaman "
    "son çalıştı, başarı oranı ne, hangi hatalar birikiyor ve ne kadar sayfa toplandı. "
    "Aynı ekranda crawl'ı başlatıp durdurabilirsiniz. Bu ekran veritabanına kayıt "
    "yazmaz; yalnız 0050 tablolarını okur."
)

BOS_ROZETI = "Henüz kazıma yapılmadı"

ETIKET_AUDIT = "Kaynak: scrape_audit_log · canlı"
ETIKET_ERRORS = "Kaynak: scrape_errors · canlı"
ETIKET_PAGES = "Kaynak: scrape_pages · canlı"

# ---------------------------------------------------------------------------
# Crawl Kontrolü (UI-ADMIN-CRAWL-TASI-35)
#
# `webhook_monitor.py`'den **taşındı**, kopyalanmadı (D-211 ikiz yasağı):
# admin crawl'i "kazıma" olarak arar, "webhook" olarak değil. Sabitler ve iki
# yardımcı burada tek tanımlıdır; eski dosyada ikinci tanım kalmadı.
# Davranış değişmedi — yalnız yer değişti.
# ---------------------------------------------------------------------------
CRAWL_STATUS_BEKLEMEDE = "beklemede"
CRAWL_STATUS_CALISIYOR = "calisiyor"
CRAWL_STATUS_BASARISIZ = "basarisiz"
CRAWL_STATUS_DURDURULDU = "durduruldu"

CRAWL_ENABLED = os.getenv("CRAWL_ENABLED", "0") == "1"

CRAWL_DURUM_IKONLARI = {
    CRAWL_STATUS_BEKLEMEDE: "⏳",
    CRAWL_STATUS_CALISIYOR: "🟢",
    CRAWL_STATUS_BASARISIZ: "🔴",
    CRAWL_STATUS_DURDURULDU: "⏸️",
}

def _crawl_is_enabled() -> bool:
    """Crawl kontrolünün etkin olup olmadığını döndürür."""
    return CRAWL_ENABLED

def _log_crawl_action(action: str, task_id: str | None = None) -> None:
    """Crawl eylemini loglar. TODO: admin_audit altyapısı gelince gerçek log yaz."""
    # TODO: API-ADMIN-SUPHELI-AKTIVITE-21 ile hizalanacak admin_audit yazılacak
    import logging

    logger = logging.getLogger("crawl_control")
    msg = f"Crawl eylemi: {action}"
    if task_id:
        msg += f" | Görev: {task_id}"
    logger.info(msg)

_0050_TABLOLAR = ("scrape_audit_log", "scrape_errors", "scrape_pages")

def _bolum(kimlik: str) -> Section:
    """Kimliğe göre bölüm tanımını getirir (anchor tutarlılığı için)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")

def _zaman_metni(ham: Any) -> str | None:
    """DB'den gelen zaman damgasını ISO metnine çevirir."""
    if ham is None:
        return None
    if isinstance(ham, datetime):
        return ham.isoformat()
    return str(ham)

# ---------------------------------------------------------------------------
# DB okuma (salt SELECT)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def load_kaynak_ozeti() -> list[dict[str, Any]]:
    """Kaynak başına toplam/başarılı çekiş, son çalışma zamanı ve son 10 çekişin durumu."""
    engine = get_engine()
    if not tablo_var_mi("scrape_audit_log", engine):
        return []
    sql = text(
        """
        SELECT source_name,
               COUNT(*) AS toplam,
               COUNT(*) FILTER (WHERE status = 'success') AS basarili,
               MAX(timestamp) AS son_zaman
          FROM scrape_audit_log
         WHERE source_name IS NOT NULL
         GROUP BY source_name
         ORDER BY MAX(timestamp) DESC
        """
    )
    with engine.connect() as conn:
        kaynaklar = [
            {
                "kaynak_id": satir["source_name"],
                "kaynak_adi": satir["source_name"],
                "toplam_cekis": int(satir["toplam"] or 0),
                "basarili_cekis": int(satir["basarili"] or 0),
                "son_cekis_zaman": _zaman_metni(satir["son_zaman"]),
            }
            for satir in conn.execute(sql).mappings()
        ]
        son_durumlar = conn.execute(text(
            """
            SELECT source_name, status
              FROM scrape_audit_log
             WHERE source_name IS NOT NULL
             ORDER BY timestamp DESC
             LIMIT 400
            """
        )).mappings().all()

    sonraki: dict[str, list[bool]] = {}
    for satir in son_durumlar:
        gid = satir["source_name"]
        if len(sonraki.setdefault(gid, [])) < 10:
            sonraki[gid].append(satir["status"] == "success")
    for kaynak in kaynaklar:
        kaynak["son_n_cekisler"] = sonraki.get(kaynak["kaynak_id"], [])
    return kaynaklar

@st.cache_data(ttl=60)
def load_son_calismalar(limit: int = 20) -> list[dict[str, Any]]:
    """En son kazıma denemeleri (salt okuma)."""
    engine = get_engine()
    if not tablo_var_mi("scrape_audit_log", engine):
        return []
    sql = text(
        """
        SELECT timestamp, source_name, action, status,
               duration_ms, bytes_fetched, llm_used, cost_usd, error_msg
          FROM scrape_audit_log
         ORDER BY timestamp DESC
         LIMIT :limit
        """
    )
    with engine.connect() as conn:
        return [
            {**dict(satir), "timestamp": _zaman_metni(satir["timestamp"])}
            for satir in conn.execute(sql, {"limit": int(limit)}).mappings()
        ]

@st.cache_data(ttl=60)
def load_son_hatalar(limit: int = 20) -> list[dict[str, Any]]:
    """En son 20 kazıma hatası; kaynak adı audit kaydından gelir."""
    engine = get_engine()
    if not tablo_var_mi("scrape_errors", engine):
        return []
    sql = text(
        """
        SELECT e.created_at, e.error_code, e.error_message,
               e.retry_count, e.fallback_tried,
               COALESCE(a.source_name, '-') AS source_name,
               COALESCE(a.source_url, '-') AS source_url
          FROM scrape_errors e
          LEFT JOIN scrape_audit_log a ON a.audit_id = e.audit_id
         ORDER BY e.created_at DESC
         LIMIT :limit
        """
    )
    with engine.connect() as conn:
        return [
            {**dict(satir), "created_at": _zaman_metni(satir["created_at"])}
            for satir in conn.execute(sql, {"limit": int(limit)}).mappings()
        ]

@st.cache_data(ttl=60)
def load_toplanan_sayfalar() -> list[dict[str, Any]]:
    """Kaynak (domain) başına toplanan sayfa adedi, ham veri hacmi ve maliyet."""
    engine = get_engine()
    if not tablo_var_mi("scrape_pages", engine):
        return []
    sql = text(
        """
        SELECT split_part(split_part(source_url, '://', 2), '/', 1) AS alan_adi,
               COUNT(*) AS sayfa_adedi,
               COALESCE(SUM(raw_content_length), 0) AS ham_bayt,
               COUNT(*) FILTER (WHERE llm_used) AS llm_kullanilan,
               COALESCE(SUM(cost_usd), 0) AS maliyet,
               MAX(fetch_timestamp) AS son_zaman
          FROM scrape_pages
         WHERE source_url IS NOT NULL
         GROUP BY 1
         ORDER BY COUNT(*) DESC
        """
    )
    with engine.connect() as conn:
        return [
            {
                "alan_adi": satir["alan_adi"],
                "sayfa_adedi": int(satir["sayfa_adedi"] or 0),
                "ham_bayt": int(satir["ham_bayt"] or 0),
                "llm_kullanilan": int(satir["llm_kullanilan"] or 0),
                "maliyet": float(satir["maliyet"] or 0.0),
                "son_zaman": _zaman_metni(satir["son_zaman"]),
            }
            for satir in conn.execute(sql).mappings()
        ]

# ---------------------------------------------------------------------------
# Saf (DB'siz) dönüşüm yardımcıları — testlerin doğrudan çağırdığı katman
# ---------------------------------------------------------------------------

def kaynak_saglik_kartlari(kaynaklar: list[dict[str, Any]]) -> list[Any]:
    """Ham kaynak satırlarını `KaynakSaglik` nesnelerine çevirir (boş girdi → boş liste)."""
    return [
        kaynak_guvenilirlik.hesapla(
            kaynak_id=kaynak.get("kaynak_id", ""),
            kaynak_adi=kaynak.get("kaynak_adi", ""),
            toplam_cekis=int(kaynak.get("toplam_cekis", 0) or 0),
            basarili_cekis=int(kaynak.get("basarili_cekis", 0) or 0),
            son_cekis_zaman=kaynak.get("son_cekis_zaman"),
            son_n_cekisler=kaynak.get("son_n_cekisler") or [],
        )
        for kaynak in kaynaklar
    ]

# D-212 tek kapı: 0-1/0-100 köprüsü kaynak_guvenilirlik.saglik_rozeti_yuzde() içinde yaşar.
saglik_rozet_metni = kaynak_guvenilirlik.saglik_rozeti_yuzde

def basari_orani(toplam: int, basarili: int) -> float:
    """Başarı oranı 0-1; çekiş yoksa 0.0 (D-249: veri yok ≠ başarısız)."""
    if toplam <= 0:
        return 0.0
    return round(basarili / toplam, 4)

def ozet_metin(kaynaklar: list[dict[str, Any]], hatalar: list[dict[str, Any]],
               sayfalar: list[dict[str, Any]]) -> str:
    """Üç bloğun tek satırlık canlı özet metni (rapor/raporlama için)."""
    if not kaynaklar and not hatalar and not sayfalar:
        return BOS_ROZETI
    toplam_cekis = sum(int(k.get("toplam_cekis", 0) or 0) for k in kaynaklar)
    toplam_basari = sum(int(k.get("basarili_cekis", 0) or 0) for k in kaynaklar)
    toplam_sayfa = sum(int(s.get("sayfa_adedi", 0) or 0) for s in sayfalar)
    return (
        f"{len(kaynaklar)} kaynak · {toplam_cekis} çekiş "
        f"({toplam_basari} başarılı) · {len(hatalar)} hata · {toplam_sayfa} sayfa"
    )

# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def _render_baslik() -> None:
    """ADMIN-UI-10: Playground kalıbı — üst etiket -> H1 -> giriş -> aksiyon."""
    PageHeader("Veri Kaynakları", giris=GIRIS_METNI,
               ust_etiket="Metrikler · Veri Kaynakları", ikon="🕷️").render()

    # K3-10g: rehber anahtarı sayfa altında (`app.REHBER_KEY`); modül yalnız okur.

    SectionNav(BOLUMLER, yatay=True).render()

def _render_durum_ozeti(kaynaklar: list[dict[str, Any]]) -> None:
    _bolum("durum-ozeti").render()
    if not kaynaklar:
        st.info(BOS_ROZETI)
        st.caption(ETIKET_AUDIT)
        return

    kartlar = kaynak_saglik_kartlari(kaynaklar)
    for kart in kartlar:
        oran = basari_orani(kart.toplam_cekis, kart.basarili_cekis)
        kpi_karti(
            f"🕷️ {kart.kaynak_adi}",
            f"{kart.skor:.1f}%",
            ikon="✅" if saglik_rozet_metni(kart.skor) == "Sağlıklı" else "⚠️",
            kategori="basari" if saglik_rozet_metni(kart.skor) == "Sağlıklı" else "uyari",
            yardim=f"{saglik_rozet_metni(kart.skor)} · {kart.basarili_cekis}/{kart.toplam_cekis} "
                   f"başarılı ({oran:.1%}) · son çekiş: {kart.son_cekis_zaman or '-'}",
            anahtar=f"kaynak-saglik-{kart.kaynak_id}",
        )
        st.caption(
            f"🟢 **GERÇEK VERİ**: {kart.kaynak_adi} · tazelik {kart.tazelik_skoru:.0f}% · "
            f"tutarlılık {kart.tutarlilik_skoru:.0f}% · hata oranı {kart.hata_orani:.1%}"
        )
    st.caption(ETIKET_AUDIT)

def _render_crawl_kontrolu() -> None:
    """Crawl başlat/durdur paneli (webhook_monitor'dan taşındı, seviye-3 alt başlık)."""
    Section("🕷️ Crawl Kontrolü",
            "Crawl'ı başlat veya durdur; durum anlık olarak aşağıda yazılır.",
            ikon="🕷️", kimlik="crawl-kontrolu", seviye=3).render()

    # Admin yetkisi kontrolü (basit: session_state'te admin_email varsa)
    is_admin = st.session_state.get("admin_email", "") != ""

    if "crawl_status" not in st.session_state:
        st.session_state["crawl_status"] = CRAWL_STATUS_BEKLEMEDE

    crawl_status = st.session_state["crawl_status"]
    crawl_enabled = _crawl_is_enabled()

    # Yetkisiz kullanıcılar için sadece okuma
    disabled_for_role = not is_admin

    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        st.checkbox(
            "Crawl etkin (ENV)",
            value=crawl_enabled,
            disabled=True,
            help="CRAWL_ENABLED environment variable ile kontrol edilir",
            key="kaynaklar_crawl_env",
        )
    with c2:
        if crawl_status in (CRAWL_STATUS_BEKLEMEDE, CRAWL_STATUS_BASARISIZ,
                            CRAWL_STATUS_DURDURULDU):
            if st.button("▶️ Crawl Başlat", disabled=disabled_for_role,
                         key="kaynaklar_crawl_baslat"):
                st.session_state["crawl_status"] = CRAWL_STATUS_CALISIYOR
                _log_crawl_action("start")
                st.success("Crawl başlatıldı")
                st.rerun()
    with c3:
        if crawl_status == CRAWL_STATUS_CALISIYOR:
            if "crawl_stop_confirm" not in st.session_state:
                st.session_state["crawl_stop_confirm"] = False

            if not st.session_state["crawl_stop_confirm"]:
                if st.button("⏹️ Crawl Durdur", disabled=disabled_for_role,
                             key="kaynaklar_crawl_durdur"):
                    st.session_state["crawl_stop_confirm"] = True
                    st.rerun()
            else:
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("✅ Evet, Durdur", type="primary", disabled=disabled_for_role,
                                 key="kaynaklar_crawl_durdur_evet"):
                        st.session_state["crawl_status"] = CRAWL_STATUS_DURDURULDU
                        st.session_state["crawl_stop_confirm"] = False
                        _log_crawl_action("stop")
                        st.success("Crawl durduruldu")
                        st.rerun()
                with cc2:
                    if st.button("❌ İptal", disabled=disabled_for_role,
                                 key="kaynaklar_crawl_durdur_iptal"):
                        st.session_state["crawl_stop_confirm"] = False
                        st.rerun()

    ikon = CRAWL_DURUM_IKONLARI.get(crawl_status, "⚪")
    st.caption(f"Mevcut durum: {ikon} {crawl_status.upper()}")

def _render_son_calismalar(calismalar: list[dict[str, Any]]) -> None:
    _bolum("son-calismalar").render()
    if not calismalar:
        st.info(BOS_ROZETI)
        st.caption(ETIKET_AUDIT)
        return

    kpi_karti("🧾 Son çalışma sayısı", len(calismalar), ikon="🧾",
              kategori="marka", anahtar="kaynak-son-calisma")
    st.dataframe(calismalar, width="stretch", hide_index=True)
    st.caption(ETIKET_AUDIT)

def _render_hatalar(hatalar: list[dict[str, Any]]) -> None:
    _bolum("hatalar").render()
    if not hatalar:
        st.success("Son 20 kayıtta hata yok.")
        st.caption(ETIKET_ERRORS)
        return

    kpi_karti("⚠️ Son hata sayısı", len(hatalar), ikon="⚠️", kategori="uyari",
              anahtar="kaynak-hata")
    st.dataframe(hatalar, width="stretch", hide_index=True)
    st.caption(ETIKET_ERRORS)

def _render_toplanan_sayfalar(sayfalar: list[dict[str, Any]]) -> None:
    _bolum("toplanan-sayfalar").render()
    if not sayfalar:
        st.info(BOS_ROZETI)
        st.caption(ETIKET_PAGES)
        return

    toplam_sayfa = sum(s["sayfa_adedi"] for s in sayfalar)
    kpi_karti("📄 Toplanan sayfa", toplam_sayfa, ikon="📄", kategori="marka",
              anahtar="kaynak-sayfa")
    st.dataframe(sayfalar, width="stretch", hide_index=True)
    st.caption(ETIKET_PAGES)

def render_kaynaklar_tab() -> None:
    """0050 kazıma tablolarını okuyan "Veri Kaynakları" ekranı (salt okuma)."""
    _render_baslik()

    try:
        kaynaklar = load_kaynak_ozeti()
        calismalar = load_son_calismalar()
        hatalar = load_son_hatalar()
        sayfalar = load_toplanan_sayfalar()
    except Exception as exc:  # noqa: BLE001 - panel bir sekmede patlamamali
        st.error(f"0050 kazıma tabloları okunamadı: {exc}")
        st.caption("Kaynak: scrape_audit_log / scrape_errors / scrape_pages · okuma hatası")
        return

    st.caption(f"🟢 **GERÇEK VERİ**: {ozet_metin(kaynaklar, hatalar, sayfalar)} "
               f"· {datetime.now().strftime('%H:%M')}")

    _render_durum_ozeti(kaynaklar)
    _render_crawl_kontrolu()
    _render_son_calismalar(calismalar)
    _render_hatalar(hatalar)
    _render_toplanan_sayfalar(sayfalar)
