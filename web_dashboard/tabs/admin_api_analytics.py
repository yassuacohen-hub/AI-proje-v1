# -*- coding: utf-8 -*-
"""P7-32 — Admin Panel Faz 2: API Analitiği sekmesi.

Kapsam:
  - Endpoint bazlı kullanım istatistikleri (çağrı sayısı)
  - En çok kullanılan endpoint'ler (top-N)
  - Tier bazlı kullanım dağılımı (terminal/strategic/enterprise)
  - Tier bazlı rate-limit yapılandırması
  - Genel sistem metrikleri (sorgu sayısı, cache hit oranı) — destekleyici bağlam

Bilinen Kısıtlar (kullanıcıya UI üzerinden açıkça bildirilir):
  - /api/admin/api-usage verisi BELLEK-İÇİ tutulur; sunucu yeniden
    başlatıldığında sıfırlanır (kalıcı/geçmiş veri değildir).
  - Sadece "enterprise" tier istekleri sayaca işlenir (bkz. web_app.py
    require_api_key -> _record_api_usage çağrısı); terminal/strategic
    tier istekleri bu sayaçta görünmez.
  - Endpoint bazlı response time / hata oranı / rate-limit tetiklenme
    OLAYI şu an backend'de ayrı ayrı izlenmiyor (yalnızca toplam DB
    sorgu süresi ve toplam istek sayısı /metrics üzerinden mevcut).
    Bu nedenle bu sekme mevcut altyapıyla sağlanabilecek en zengin
    görünümü sunar; response-time/hata-oranı için backend'e yeni
    telemetri eklenmesi ayrı bir kapsam kararı gerektirir.

Kurallar:
  - st.cache_data ttl=30
  - st.metric kullanımı
  - /api/admin/api-usage ve /metrics endpoint'lerini kullan
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from scripts.dash04_api_client import get_api, APIError  # noqa: E402
from web_dashboard.tabs.admin_auth import get_admin_token  # noqa: E402


@st.cache_data(ttl=30)
def load_api_usage(token: str | None) -> dict[str, Any]:
    """/api/admin/api-usage endpoint'inden tier -> endpoint -> sayac verisini yukle."""
    try:
        data = get_api("/api/admin/api-usage", token=token)
        if isinstance(data, dict):
            return {
                "items": data.get("items", {}) or {},
                "rate_limits": data.get("rate_limits", {}) or {},
            }
    except (APIError, Exception):
        pass
    return {"items": {}, "rate_limits": {}}


@st.cache_data(ttl=30)
def load_metrics_summary() -> dict[str, Any]:
    """/metrics endpoint'inden destekleyici sistem metriklerini yukle."""
    try:
        data = get_api("/metrics")
        if isinstance(data, dict) and data:
            return data
    except (APIError, Exception):
        pass
    return {}


def _flatten_usage(items: dict[str, dict[str, int]]) -> pd.DataFrame:
    """tier -> endpoint -> count sozlugunu duz DataFrame'e cevirir."""
    rows: list[dict[str, Any]] = []
    for tier, endpoints in (items or {}).items():
        if not isinstance(endpoints, dict):
            continue
        for endpoint, count in endpoints.items():
            rows.append({"tier": tier, "endpoint": endpoint, "cagri_sayisi": count})
    if not rows:
        return pd.DataFrame(columns=["tier", "endpoint", "cagri_sayisi"])
    return pd.DataFrame(rows)


def render_api_analytics_tab() -> None:
    """P7-32: API Analitiği sekmesini gosterir."""
    st.subheader("🔌 API Analitiği")

    st.info(
        "ℹ️ Bu veriler **bellek-içi** tutulur ve sunucu yeniden başlatıldığında "
        "sıfırlanır. Şu an yalnızca **enterprise** tier istekleri sayaca işleniyor; "
        "endpoint bazlı response time / hata oranı / rate-limit tetiklenme olayı "
        "backend'de henüz ayrı izlenmiyor."
    )

    token = get_admin_token()

    with st.spinner("API kullanım verisi yükleniyor..."):
        usage = load_api_usage(token)
        metrics = load_metrics_summary()

    items = usage.get("items", {})
    rate_limits = usage.get("rate_limits", {})
    df = _flatten_usage(items)

    # --- Özet metrikler ---
    toplam_cagri = int(df["cagri_sayisi"].sum()) if not df.empty else 0
    distinct_endpoint = int(df["endpoint"].nunique()) if not df.empty else 0
    en_cok_kullanilan = ""
    if not df.empty:
        top_row = df.groupby("endpoint")["cagri_sayisi"].sum().idxmax()
        en_cok_kullanilan = str(top_row)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Toplam Çağrı", f"{toplam_cagri:,}".replace(",", "."))
    with c2:
        st.metric("Farklı Endpoint", distinct_endpoint)
    with c3:
        st.metric("En Çok Kullanılan", en_cok_kullanilan or "—")
    with c4:
        st.metric("İzlenen Tier Sayısı", len(items) if items else 0)

    st.divider()

    # --- En çok kullanılan endpointler ---
    st.markdown("### 📈 En Çok Kullanılan Endpoint'ler")
    if not df.empty:
        top_n = (
            df.groupby("endpoint")["cagri_sayisi"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(top_n)
        st.dataframe(
            top_n.reset_index().rename(
                columns={"endpoint": "Endpoint", "cagri_sayisi": "Çağrı Sayısı"}
            ),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("Henüz kaydedilmiş API kullanım verisi yok.")

    st.divider()

    # --- Tier bazlı kullanım dağılımı ---
    st.markdown("### 👥 Tier Bazlı Kullanım Dağılımı")
    if not df.empty:
        tier_toplam = df.groupby("tier")["cagri_sayisi"].sum().sort_values(ascending=False)
        col_chart, col_table = st.columns([2, 1])
        with col_chart:
            st.bar_chart(tier_toplam)
        with col_table:
            st.dataframe(
                tier_toplam.reset_index().rename(
                    columns={"tier": "Tier", "cagri_sayisi": "Çağrı Sayısı"}
                ),
                width="stretch",
                hide_index=True,
            )
    else:
        st.info("Tier bazlı veri henüz mevcut değil.")

    st.divider()

    # --- Tier bazlı rate-limit yapılandırması ---
    st.markdown("### ⚙️ Tier Bazlı Rate-Limit Yapılandırması (istek/dakika)")
    if rate_limits:
        rl_df = pd.DataFrame(
            [{"Tier": tier, "Limit (istek/dk)": limit} for tier, limit in rate_limits.items()]
        )
        st.dataframe(rl_df, width="stretch", hide_index=True)
    else:
        st.info("Rate-limit yapılandırması alınamadı.")

    st.divider()

    # --- Destekleyici sistem metrikleri ---
    st.markdown("### 🩺 Destekleyici Sistem Metrikleri (/metrics)")
    if metrics:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Toplam Sorgu", f"{metrics.get('huginn_query_count', 0):,}".replace(",", "."))
        with m2:
            st.metric("DB Süresi (ms)", f"{metrics.get('huginn_db_time_ms', 0):,.1f}".replace(",", "."))
        with m3:
            st.metric("Cache Hit", metrics.get("huginn_cache_hits", 0))
        with m4:
            hit_rate = metrics.get("huginn_cache_hit_rate", 0)
            st.metric("Cache Hit Oranı", f"%{hit_rate * 100:.1f}")
    else:
        st.info("Sistem metrikleri alınamadı.")

    st.divider()

    # --- Rapor oluşturma ---
    if st.button("📊 API Analitik Raporu Oluştur"):
        rapor = {
            "olusturma_zamani": datetime.now().isoformat(),
            "toplam_cagri": toplam_cagri,
            "farkli_endpoint_sayisi": distinct_endpoint,
            "en_cok_kullanilan_endpoint": en_cok_kullanilan,
            "tier_dagilimi": items,
            "rate_limits": rate_limits,
            "sistem_metrikleri": metrics,
            "kisitlar": [
                "Veriler bellek-ici tutulur, sunucu restartinda sifirlanir.",
                "Sadece enterprise tier istekleri sayaca islenir.",
                "Endpoint bazli response time / hata orani su an izlenmiyor.",
            ],
        }
        st.json(rapor)
        import json as _json

        st.download_button(
            label="📥 Raporu İndir (JSON)",
            data=_json.dumps(rapor, ensure_ascii=False, indent=2),
            file_name=f"api_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )
