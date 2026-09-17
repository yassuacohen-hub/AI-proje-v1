# -*- coding: utf-8 -*-
"""P7-27 — Admin Panel Faz 2: AI Cost Dashboard sekmesi.

Işlevsellik:
  - 9router provider bazli gunluk/aylik maliyet analizi
  - Plotly charts (provider breakdown, trend, latency, anomaliler)
  - KPI kartlari ve detay tablolari
  - Streamlit entegrasyonu (@st.cache_data TTL=30s)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from web_dashboard.charts import kpi_karti


# ================================================================ Veri Modelleri
@dataclass
class ProviderCost:
    """Provider bazli maliyet + saglik metrikleri."""
    provider: str
    daily_cost_usd: float = 0.0
    daily_calls: int = 0
    daily_avg_cost_per_call: float = 0.0

    latency_ms: float = 0.0
    success_rate: float = 100.0
    error_rate: float = 0.0

    health_status: str = "OK"  # OK, WARNING, ERROR
    backoff_level: int = 0
    model_locks: int = 0

    # Provider detaylari (raw)
    name: str = ""
    is_active: bool = True
    auth_type: str = ""


@dataclass
class AnomalyFlag:
    """Anomali işareti."""
    flag_type: str  # high_cost, error, rate_limited, latency, saglik_sorunu
    severity: str   # YUKSEK, ORTA, DUSUK
    provider: str = ""
    reasons: str = ""  # nedenler listesinin okunabilir birlesimi
    value: float = 0.0
    threshold: float = 0.0
    timestamp: str = ""


@dataclass
class TrendPoint:
    """Zaman serisi noktası."""
    date: str
    cost_usd: float
    calls: int
    avg_cost_per_call: float
    anomalies_count: int


@dataclass
class CostSummary:
    """Ana ozet nesnesi."""
    timestamp: str
    total_daily_cost_usd: float = 0.0
    total_daily_calls: int = 0
    total_avg_cost_per_call: float = 0.0

    estimated_monthly_cost_usd: float = 0.0

    providers: list[ProviderCost] = field(default_factory=list)
    anomalies: list[AnomalyFlag] = field(default_factory=list)
    trend: list[TrendPoint] = field(default_factory=list)

    provider_count: int = 0
    active_provider_count: int = 0
    problematic_provider_count: int = 0


# ================================================================ Veri Yükleme
def _empty_cost_summary() -> CostSummary:
    """Bos CostSummary fallback."""
    return CostSummary(
        timestamp=datetime.now().isoformat(),
        total_daily_cost_usd=0.0,
        total_daily_calls=0,
        total_avg_cost_per_call=0.0,
        estimated_monthly_cost_usd=0.0,
        providers=[],
        anomalies=[],
        trend=[],
        provider_count=0,
        active_provider_count=0,
        problematic_provider_count=0,
    )


@st.cache_data(ttl=30)
def load_cost_summary() -> CostSummary:
    """9router_optimizer.py'nin urettigi JSON'dan CostSummary yukle.

    Veri kaynagi: data/router/optimizer_latest.json

    Fallback: Bos ozet (UI crash değil)
    """
    try:
        json_path = Path("data/router/optimizer_latest.json")
        if not json_path.exists():
            return _empty_cost_summary()

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Timestamp al
        ts = data.get("timestamp", datetime.now().isoformat())

        # GERÇEK YAPI (9router_optimizer.py json_cikti()):
        # - saglik.providerlar  -> tum providerlarin durum/saglik bilgisi
        # - skorlar             -> provider bazli latency_ms / maliyet_ort_usd
        # - anomaliler          -> provider/name/nedenler(list)/oncelik
        # - combo_istatistik.usageHistory     -> toplam_maliyet_usd, provider_maliyet_toplam,
        #                                        provider_maliyet_ort, provider_cagri_sayisi
        # - combo_istatistik.requestDetails   -> provider_latency_ort, provider_status
        combo = data.get("combo_istatistik", {})
        usage = combo.get("usageHistory", {})
        total_cost = float(usage.get("toplam_maliyet_usd", 0.0))
        provider_costs_raw = usage.get("provider_maliyet_toplam", {})
        provider_calls = usage.get("provider_cagri_sayisi", {})
        provider_costs_avg = usage.get("provider_maliyet_ort", {})

        req_detail = combo.get("requestDetails", {})
        prov_latency = req_detail.get("provider_latency_ort", {})
        prov_status = req_detail.get("provider_status", {})

        # saglik.providerlar -> tum tanimli providerlar (31 adet); usageHistory sadece
        # gercekte cagrilan birkac provider'i icerir, digerlerinde maliyet/cagri 0 kalir.
        providerlar = data.get("saglik", {}).get("providerlar", [])

        # skorlar -> latency_ms / maliyet_ort_usd icin fallback kaynagi (combo disi providerlar icin)
        skorlar_raw = data.get("skorlar", [])
        skor_lookup: dict[str, dict] = {
            s.get("provider"): s for s in skorlar_raw if s.get("provider")
        }

        # Provider listesi olustur
        providers: list[ProviderCost] = []
        provider_set = set()

        for p in providerlar:
            pname = p.get("provider", "unknown")
            provider_set.add(pname)
            skor = skor_lookup.get(pname, {})

            cost_total = float(provider_costs_raw.get(pname, 0.0))
            calls = int(provider_calls.get(pname, 0) or 0)
            cost_avg_raw = provider_costs_avg.get(pname)
            cost_avg = float(cost_avg_raw) if cost_avg_raw is not None else float(skor.get("maliyet_ort_usd") or 0.0)
            latency_raw = prov_latency.get(pname)
            latency = float(latency_raw) if latency_raw is not None else float(skor.get("latency_ms") or 0.0)

            # Status oranları
            stat = prov_status.get(pname, {})
            success = stat.get("success", 0)
            error = stat.get("error", 0)
            total_req = success + error
            success_rate = (success / total_req * 100) if total_req > 0 else 100.0
            error_rate = (error / total_req * 100) if total_req > 0 else 0.0

            # Saglik durumu
            durum = p.get("durum", {})
            backoff = durum.get("backoffLevel") or 0
            locks = durum.get("modelLockSayisi") or 0

            health = "OK"
            if backoff >= 5 or locks > 10 or durum.get("errorCode"):
                health = "ERROR"
            elif backoff >= 3 or locks > 5:
                health = "WARNING"

            pc = ProviderCost(
                provider=pname,
                daily_cost_usd=cost_total,
                daily_calls=calls,
                daily_avg_cost_per_call=cost_avg,
                latency_ms=latency,
                success_rate=success_rate,
                error_rate=error_rate,
                health_status=health,
                backoff_level=backoff,
                model_locks=locks,
                name=p.get("name", pname),
                is_active=bool(p.get("isActive", True)),
                auth_type=p.get("authType", ""),
            )
            providers.append(pc)

        # Anomaliler — gerçek alanlar: provider, name, nedenler(list[str]), oncelik
        anomalies: list[AnomalyFlag] = []
        anomali_raw = data.get("anomaliler", [])

        for a in anomali_raw:
            nedenler = a.get("nedenler", [])
            af = AnomalyFlag(
                flag_type="saglik_sorunu",
                severity=a.get("oncelik", "ORTA"),
                provider=a.get("provider", ""),
                reasons=" | ".join(nedenler) if nedenler else a.get("name", ""),
                timestamp=ts,
            )
            anomalies.append(af)

        # Ek anomaliler (hesaplı — maliyet/hata/latency bazlı, gerçek combo verisi üzerinden)
        cost_providers = [pc for pc in providers if pc.daily_cost_usd > 0]
        avg_cost = (sum(pc.daily_cost_usd for pc in cost_providers) / len(cost_providers)) if cost_providers else 0.0
        for pc in providers:
            if avg_cost > 0 and pc.daily_cost_usd > avg_cost * 2:
                severity = "YUKSEK" if pc.daily_cost_usd > avg_cost * 3 else "ORTA"
                anomalies.append(AnomalyFlag(
                    flag_type="high_cost",
                    severity=severity,
                    provider=pc.provider,
                    reasons=f"Maliyet ${pc.daily_cost_usd:.4f} ortalamanın 2 katından fazla",
                    value=pc.daily_cost_usd,
                    threshold=avg_cost * 2,
                    timestamp=ts,
                ))

            if pc.error_rate > 5:
                anomalies.append(AnomalyFlag(
                    flag_type="error",
                    severity="YUKSEK" if pc.error_rate > 20 else "ORTA",
                    provider=pc.provider,
                    reasons=f"Hata oranı %{pc.error_rate:.1f}",
                    value=pc.error_rate,
                    threshold=5.0,
                    timestamp=ts,
                ))

            if pc.latency_ms > 5000:
                anomalies.append(AnomalyFlag(
                    flag_type="latency",
                    severity="DUSUK",
                    provider=pc.provider,
                    reasons=f"Latency {pc.latency_ms:.0f}ms eşik olan 5000ms üzerinde",
                    value=pc.latency_ms,
                    threshold=5000.0,
                    timestamp=ts,
                ))

        # Trend (tahmini — 30 günlük ekstrapol; gerçek zaman serisi için arşiv gerekir)
        trend: list[TrendPoint] = []
        total_calls = sum(pc.daily_calls for pc in providers)
        tp = TrendPoint(
            date=datetime.now().strftime("%Y-%m-%d"),
            cost_usd=total_cost,
            calls=total_calls,
            avg_cost_per_call=total_cost / max(1, total_calls),
            anomalies_count=len(anomalies),
        )
        trend.append(tp)

        # Aylık tahmin
        monthly_cost = total_cost * 30

        cs = CostSummary(
            timestamp=ts,
            total_daily_cost_usd=total_cost,
            total_daily_calls=total_calls,
            total_avg_cost_per_call=total_cost / max(1, total_calls),
            estimated_monthly_cost_usd=monthly_cost,
            providers=providers,
            anomalies=anomalies,
            trend=trend,
            provider_count=len(provider_set),
            active_provider_count=len([p for p in providers if p.is_active]),
            problematic_provider_count=len([p for p in providers if p.health_status != "OK"]),
        )
        return cs

    except Exception as e:
        st.warning(f"⚠️ Maliyet verisi yükleme hatası: {e}")
        return _empty_cost_summary()


# ================================================================ Plotly Charts
def chart_provider_breakdown(cost_summary: CostSummary) -> go.Figure | None:
    """Provider-bazlı maliyet dagilimi (Pie chart).

    Top 10 provider, gerisi "Diğer" kategorisinde.
    """
    if not cost_summary.providers:
        return None

    # En yuksek 10 sırala
    top_providers = sorted(
        cost_summary.providers,
        key=lambda p: p.daily_cost_usd,
        reverse=True
    )[:10]

    labels = [p.provider for p in top_providers]
    values = [p.daily_cost_usd for p in top_providers]

    # Gerisi var mı?
    other_cost = sum(p.daily_cost_usd for p in cost_summary.providers[10:])
    if other_cost > 0:
        labels.append("Diğer")
        values.append(other_cost)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hovertemplate="<b>%{label}</b><br>Maliyet: $%{value:.4f}<br>%{percent}<extra></extra>",
    )])
    fig.update_layout(
        title="Provider-Bazlı Günlük Maliyet Dağılımı",
        height=400,
        showlegend=True,
    )
    return fig


def chart_daily_trend(cost_summary: CostSummary) -> go.Figure | None:
    """Günlük trend: Maliyet + Çağrı sayısı (dual-axis).

    Şimdilik tek nokta (günümüz verisi).
    Gelecek: Archive JSON'lar arşivlenerek gerçek zaman serisi.
    """
    if not cost_summary.trend:
        return None

    trend = cost_summary.trend
    dates = [t.date for t in trend]
    costs = [t.cost_usd for t in trend]
    calls = [t.calls for t in trend]

    fig = go.Figure()

    # Maliyet (sol axis)
    fig.add_trace(go.Bar(
        x=dates,
        y=costs,
        name="Günlük Maliyet (USD)",
        marker=dict(color="rgba(99, 110, 250, 0.6)"),
        yaxis="y",
    ))

    # Çağrılar (sağ axis)
    fig.add_trace(go.Scatter(
        x=dates,
        y=calls,
        name="Çağrı Sayısı",
        mode="lines+markers",
        marker=dict(color="red", size=8),
        yaxis="y2",
    ))

    fig.update_layout(
        title="Günlük Maliyet ve Çağrı Trendi",
        height=400,
        hovermode="x unified",
        yaxis=dict(title="Maliyet (USD)"),
        yaxis2=dict(title="Çağrılar", overlaying="y", side="right"),
        xaxis=dict(title="Tarih"),
    )
    return fig


def chart_latency_vs_cost(cost_summary: CostSummary) -> go.Figure | None:
    """Latency vs Maliyet scatter (bubble).

    X: Latency (ms)
    Y: Maliyet (USD)
    Bubble size: Çağrı sayısı
    Renk: Sağlık durumu
    """
    if not cost_summary.providers:
        return None

    prov = cost_summary.providers
    x_data = [p.latency_ms for p in prov]
    y_data = [p.daily_cost_usd for p in prov]
    size_data = [max(1, p.daily_calls / 10) for p in prov]  # Scale down for visibility
    color_map = {"OK": "green", "WARNING": "orange", "ERROR": "red"}
    colors = [color_map.get(p.health_status, "blue") for p in prov]
    labels = [p.provider for p in prov]

    fig = go.Figure(data=[go.Scatter(
        x=x_data,
        y=y_data,
        mode="markers",
        marker=dict(
            size=size_data,
            color=colors,
            opacity=0.7,
            line=dict(width=1),
        ),
        text=labels,
        hovertemplate="<b>%{text}</b><br>Latency: %{x:.1f}ms<br>Maliyet: $%{y:.4f}<extra></extra>",
    )])
    fig.update_layout(
        title="Latency vs Maliyet (Bubble size = Çağrı Sayısı)",
        xaxis_title="Latency (ms)",
        yaxis_title="Günlük Maliyet (USD)",
        height=400,
    )
    return fig


def chart_anomaly_flags(cost_summary: CostSummary) -> go.Figure | None:
    """Anomali flagleri: Tipi × Sayı (Bar chart).

    Renklendirilme: Ciddiyet (kırmızı/turuncu/sarı).
    """
    if not cost_summary.anomalies:
        return None

    # Tiptesine gore say
    anomaly_counts = {}
    for a in cost_summary.anomalies:
        anomaly_counts[a.flag_type] = anomaly_counts.get(a.flag_type, 0) + 1

    types = list(anomaly_counts.keys())
    counts = list(anomaly_counts.values())

    # Ciddiyet: Tipi sorgusu (ortalama ciddiyet alici)
    severity_map = {
        "high_cost": "ORTA",
        "error": "YUKSEK",
        "rate_limited": "YUKSEK",
        "latency": "DUSUK",
    }
    colors = []
    for t in types:
        sev = severity_map.get(t, "DUSUK")
        if sev == "YUKSEK":
            colors.append("red")
        elif sev == "ORTA":
            colors.append("orange")
        else:
            colors.append("yellow")

    fig = go.Figure(data=[go.Bar(
        x=types,
        y=counts,
        marker=dict(color=colors),
        hovertemplate="<b>%{x}</b><br>Sayı: %{y}<extra></extra>",
    )])
    fig.update_layout(
        title="Anomali Flagleri (Tiptesine Göre)",
        xaxis_title="Anomali Tipi",
        yaxis_title="Sayı",
        height=300,
    )
    return fig


def chart_cost_efficiency(cost_summary: CostSummary) -> go.Figure | None:
    """Maliyet Verimliliği Heatmap: Provider × Metrik.

    Metrikler: Cost/Call, Success Rate, Latency
    """
    if not cost_summary.providers:
        return None

    prov = cost_summary.providers[:10]  # Top 10
    providers = [p.provider for p in prov]

    # Normalizasyon için max değerler
    max_cost_per_call = max((p.daily_avg_cost_per_call for p in prov), default=1.0) or 1.0

    # Metrikler (0-1 ölçeğine normalize et)
    cost_per_call_norm = [p.daily_avg_cost_per_call / max_cost_per_call for p in prov]
    success_rate_norm = [p.success_rate / 100.0 for p in prov]
    latency_norm = [min(1.0, p.latency_ms / 5000.0) for p in prov]

    z_data = [
        cost_per_call_norm,
        success_rate_norm,
        latency_norm,
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=providers,
        y=["Cost/Call", "Success Rate", "Latency Norm"],
        colorscale="RdYlGn_r",
        hovertemplate="%{y} | %{x}: %{z:.2%}<extra></extra>",
    ))
    fig.update_layout(
        title="Maliyet Verimliliği Heatmap (Provider × Metrik)",
        height=300,
    )
    return fig


# ================================================================ Streamlit UI
def render_cost_tab() -> None:
    """Admin sekmesi: AI Cost Dashboard."""
    st.header("💰 AI Maliyet Dashboard")

    # Veri yükle
    cost_summary = load_cost_summary()

    if cost_summary.provider_count == 0:
        st.info("⏳ Henüz maliyet verisi yok. Optimizer'ı çalıştırın: `python scripts/9router_optimizer.py`")
        return

    # === KPI Kartları ===
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_karti(
            "Günlük Maliyet",
            f"${cost_summary.total_daily_cost_usd:.4f}",
            delta=f"Aylık: ${cost_summary.estimated_monthly_cost_usd:.2f}",

            kategori="maliyet",
        )

    with col2:
        kpi_karti(
            "Günlük Çağrılar",
            f"{cost_summary.total_daily_calls:,}",
            delta=f"Ort: ${cost_summary.total_avg_cost_per_call:.6f}",

            kategori="maliyet",
        )

    with col3:
        kpi_karti(
            "Aktif Providerlar",
            cost_summary.active_provider_count,
            delta=f"Toplam: {cost_summary.provider_count}",
            kategori="maliyet",
        )

    with col4:
        kpi_karti(
            "Sorunlu Providerlar",
            cost_summary.problematic_provider_count,
            delta_color="inverse",
            kategori="maliyet",
        )

    st.divider()

    # === Grafikler ===
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_pie = chart_provider_breakdown(cost_summary)
        if fig_pie:
            st.plotly_chart(fig_pie, width="stretch")
        else:
            st.bar_chart({"Provider": [0]})

    with chart_col2:
        fig_trend = chart_daily_trend(cost_summary)
        if fig_trend:
            st.plotly_chart(fig_trend, width="stretch")
        else:
            st.info("Trend verisi henüz mevcut değil.")

    # Scatter + Anomali
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        fig_scatter = chart_latency_vs_cost(cost_summary)
        if fig_scatter:
            st.plotly_chart(fig_scatter, width="stretch")

    with chart_col4:
        fig_anomaly = chart_anomaly_flags(cost_summary)
        if fig_anomaly:
            st.plotly_chart(fig_anomaly, width="stretch")

    # Heatmap
    st.subheader("Verimliliği Heatmap")
    fig_heatmap = chart_cost_efficiency(cost_summary)
    if fig_heatmap:
        st.plotly_chart(fig_heatmap, width="stretch")

    st.divider()

    # === Provider Detay Tablosu ===
    st.subheader("Provider Detayları")

    provider_data = []
    for p in cost_summary.providers:
        provider_data.append({
            "Provider": p.provider,
            "Günlük Maliyet": f"${p.daily_cost_usd:.4f}",
            "Çağrılar": p.daily_calls,
            "Ort Cost/Call": f"${p.daily_avg_cost_per_call:.6f}",
            "Latency (ms)": f"{p.latency_ms:.1f}",
            "Success %": f"{p.success_rate:.1f}%",
            "Error %": f"{p.error_rate:.1f}%",
            "Durumu": p.health_status,
            "Backoff": p.backoff_level,
            "Locks": p.model_locks,
        })

    if provider_data:
        st.dataframe(provider_data, width="stretch")

    st.divider()

    # === Anomaliler ===
    if cost_summary.anomalies:
        st.subheader("⚠️ Tespit Edilen Anomaliler")

        anomaly_data = []
        for a in cost_summary.anomalies:
            anomaly_data.append({
                "Tipi": a.flag_type,
                "Öncelik": a.severity,
                "Provider": a.provider or "—",
                "Neden(ler)": a.reasons or f"{a.value:.2f} (eşik: {a.threshold:.2f})",
                "Zaman": a.timestamp,
            })

        st.dataframe(anomaly_data, width="stretch")
    else:
        st.success("✅ Anomali tespit edilmedi.")

    # === Metadata ===
    with st.expander("📋 Metadata"):
        st.caption(f"**Güncellenme Zamanı:** {cost_summary.timestamp}")
        st.caption(f"**Kaynağı:** data/router/optimizer_latest.json")
        st.caption(f"**Cache TTL:** 30 saniye")
