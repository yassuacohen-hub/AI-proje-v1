# P7-27: AI Cost Dashboard Mimarisi — Detaylı Implementasyon Planı

**Görev:** Admin Panel Faz 2 — AI Cost sekmesini app.py'ye entegre et
- Provider-bazlı günlük/aylık maliyet analizi
- Model breakdown ve anomali tespiti
- Plotly charts ile görselleştirme
- Kalite Özeti ve API Analytics sekmelerine bağlantı

**Tarih:** 2026-09-13
**Versiyon:** V1 (Mimari Tasarım)

---

## 📊 Cevaplandırılan Sorular

### 1. 9router_optimizer.py Çıktıları

**Ana JSON Dosyası:** [`data/router/optimizer_latest.json`](../../data/router/optimizer_latest.json)

**Maliyet Alanları:**
```json
{
  "combo_istatistik": {
    "usageHistory": {
      "toplam_maliyet_usd": 12.45,                    // Toplam günlük (son 500 kayıt)
      "provider_maliyet_toplam": {                    // Provider-bazlı toplam
        "openrouter": 5.23,
        "kiro": 4.12,
        "cloudflare-ai": 3.10
      },
      "provider_maliyet_ort": {                       // Provider-bazlı ortalama/çağrı
        "openrouter": 0.00116,
        "kiro": 0.00137,
        "cloudflare-ai": 0.00089
      },
      "provider_cagri_sayisi": {                      // Provider başına çağrı sayısı
        "openrouter": 450,
        "kiro": 300,
        "cloudflare-ai": 348
      }
    }
  },
  "skorlar": [                                         // Provider skor tablosu
    {
      "provider": "openrouter",
      "latency_ms": 245.3,
      "maliyet_ort_usd": 0.00116,
      "toplam": 95.5                                  // Skor: %50 sağlık + %25 hız + %25 maliyet
    }
  ],
  "anomaliler": [                                      // Anomali tespiti
    {
      "provider": "cline",
      "nedenler": ["error=402", "locks=8"],
      "oncelik": "YUKSEK"
    }
  ]
}
```

**Yardımcı Dosyalar:**
- `data/router/optimizer_YYYYMMDD_HHMM.md` — Markdown rapor (arşiv)
- `data/router/yedekler/9router_YYYYMMDD_HHMM.sqlite` — DB yedekleri

---

### 2. app.py Admin Tab Yapısı

**Mevcut Yapı** ([`app.py:413`](../../app.py:413)):

```python
admin_tab1, ..., admin_tab9 = st.tabs([
  "📊 Sistem Durumu",      # admin_tab1
  "🔑 API Yönetimi",       # admin_tab2
  "📋 Webhook Metrikleri", # admin_tab3
  "📋 Karar Defteri",      # admin_tab4
  "👥 Kullanıcı Yönetimi", # admin_tab5
  "📈 KPI Kartları",       # admin_tab6
  "🔌 Webhook Monitor",    # admin_tab7
  "🔍 Denetim",            # admin_tab8
  "⏱️ Performans"          # admin_tab9
])
```

**Yeni Tab 10 Eklenecek:**
```python
admin_tab10 = st.tabs(...)[9]  # "💰 AI Maliyet"
```

---

### 3. Plotly Entegrasyonu

**Mevcut Durum:**
- ❌ `admin_kpi.py` → `import plotly` yok, `st.bar_chart()` kullanılıyor
- ❌ `admin_performance.py` → `import plotly` yok
- ✅ `requirements-app.txt` → Plotly muhtemelen yüklü (kontrol: `pip list | grep plotly`)

**Yeni admin_cost.py İçin:**
```python
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
```

---

### 4. Maliyet Verisi: Real-time vs Batch

**Seçim: BATCH READ** ✅

**Neden:**
- 9router_optimizer.py periyodik çalışıyor (cron/manual)
- JSON çıktısı disk'te persiste (veri kaybı riski yok)
- Real-time DB polling ağır (SQLite file-locking)
- TTL=30s cache ile yeterli (batch data güncelleme sıklığı ~saatlik)

**Akış:**
```
9router_optimizer.py (cron: saatlik)
    ↓
data/router/optimizer_latest.json
    ↓ (TTL=30s cache)
admin_cost.py.load_cost_summary()
    ↓
Streamlit UI
```

---

## 🏗️ Detaylı Mimari Tasarım

### Dosya Yapısı (Yeni)

```
web_dashboard/
├── tabs/
│   ├── admin_cost.py              ← YENİ: Maliyet sekmesi
│   │   ├── load_cost_summary()    // optimizer_latest.json oku
│   │   ├── chart_provider_breakdown()
│   │   ├── chart_daily_trend()
│   │   ├── chart_latency_vs_cost()
│   │   ├── chart_anomaly_flags()
│   │   ├── render_cost_tab()
│   │   └── render_cost_metrics()  // Kart sayıları
│   │
│   ├── admin_kpi.py               (Güncellenecek: Maliyet metric ekle)
│   └── admin_performance.py       (Güncellenecek: Dolar/çağrı metric ekle)
│
app.py                              (Güncellenecek: Tab 10 ekle + import)

data/router/                        (Veri kaynağı)
├── optimizer_latest.json
└── yedekler/
```

---

### Veri Model: CostSummary

```python
# admin_cost.py içinde tanımlı dataclass'lar

from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class ProviderCost:
    """Provider-bazlı maliyet ve sağlık metriği."""
    provider: str                     # "openrouter", "kiro", "cloudflare-ai" vb.
    name: str                         # Kullanıcı tanımlı isim ("open router ilk key")

    # Günlük maliyet (optimizer son 500 kayıt üzerinden)
    daily_cost_usd: float             # Toplam günlük maliyet
    daily_calls: int                  # Çağrı sayısı
    daily_avg_cost_per_call: float    # USD/çağrı

    # Aylık tahmin (basit 30x ekstrapol)
    monthly_cost_usd: float           # daily_cost_usd * 30
    monthly_calls: int                # daily_calls * 30

    # Performans metrikleri
    latency_ms: Optional[float]       # Ortalama latency (ms)
    success_rate: float               # % başarı
    error_rate: float                 # % hata

    # Sağlık durumu
    health_status: str                # "active", "error", "rate_limited", "unavailable"
    backoff_level: int                # 0-14
    model_locks: int                  # Kilitleme sayısı
    error_code: Optional[int]         # HTTP error kodu

@dataclass
class AnomalyFlag:
    """Anomali işareti."""
    provider: str
    name: str
    flag_type: str                    # "high_cost", "error", "rate_limited", "latency"
    severity: str                     # "YUKSEK", "ORTA", "DUSUK"
    message: str                      # "Maliyet 2x ortalaması üstü", "Backoff ≥5" vb.
    value: float                      # Ölçülen değer

@dataclass
class TrendPoint:
    """Zaman serisi noktası."""
    date: date
    cost_usd: float
    calls: int
    avg_cost_per_call: float
    anomalies_count: int

@dataclass
class CostSummary:
    """Maliyet özeti (ana dış yapı)."""
    timestamp: str                    # ISO 8601 (optimizer_latest.json'dan)
    generated_at: str                 # Oluşturma tarihi (Streamlit render)

    # Genel toplamlar
    total_cost_today_usd: float
    total_calls_today: int
    total_avg_cost_today: float       # total_cost / total_calls

    # Aylık tahmin
    total_cost_month_usd: float       # total_cost_today * 30
    total_calls_month: int

    # Provider listesi
    providers: list[ProviderCost]

    # Anomaliler
    anomalies: list[AnomalyFlag]

    # Trend (7 ve 30 günlük)
    trend_7d: list[TrendPoint]
    trend_30d: list[TrendPoint]

    # Meta
    optimizer_file: str               # "data/router/optimizer_latest.json"
    cache_ttl: int                    # 30 (saniye)
```

---

### Chart Templates (Plotly)

#### 1. Provider Breakdown (Pie Chart)

```python
def chart_provider_breakdown(summary: CostSummary, top_n: int = 10) -> go.Figure:
    """
    Pie chart: Provider-bazlı maliyet dağılımı.

    Args:
        summary: CostSummary nesnesi
        top_n: İlk N provider göster (gerisi "Diğer")

    Returns:
        Plotly Figure
    """
    # Veri hazırlama
    top_providers = sorted(summary.providers, key=lambda p: p.daily_cost_usd, reverse=True)[:top_n]
    others_cost = sum(p.daily_cost_usd for p in summary.providers[top_n:])

    labels = [p.provider for p in top_providers]
    values = [p.daily_cost_usd for p in top_providers]
    colors = [
        "green" if p.health_status == "active" else "red"
        for p in top_providers
    ]

    if others_cost > 0:
        labels.append("Diğer")
        values.append(others_cost)
        colors.append("lightgray")

    # Pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hovertemplate="<b>%{label}</b><br>$%{value:.4f}<br>%{percent}<extra></extra>",
        textposition="inside",
        textinfo="label+percent"
    )])

    fig.update_layout(
        title="💰 Provider-Bazlı Maliyet Dağılımı (Günlük)",
        height=500,
        showlegend=True
    )

    return fig
```

#### 2. Daily Trend (Line Chart)

```python
def chart_daily_trend(summary: CostSummary, days: int = 7) -> go.Figure:
    """
    Line chart: Günlük maliyet trendi.

    Args:
        summary: CostSummary nesnesi
        days: 7 veya 30 (trend_7d vs trend_30d)

    Returns:
        Plotly Figure
    """
    trend = summary.trend_7d if days == 7 else summary.trend_30d

    if not trend:
        return go.Figure().add_annotation(text="Trend verisi yok")

    dates = [t.date.isoformat() for t in trend]
    costs = [t.cost_usd for t in trend]
    calls = [t.calls for t in trend]

    # Dual-axis: Cost (bar) + Calls (line)
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )

    # Maliyet (bar)
    fig.add_trace(
        go.Bar(
            x=dates, y=costs,
            name="Maliyet USD",
            marker=dict(color="rgba(31, 119, 180, 0.8)"),
            hovertemplate="<b>%{x}</b><br>$%{y:.4f}<extra></extra>",
            secondary_y=False
        )
    )

    # Çağrı sayısı (line)
    fig.add_trace(
        go.Scatter(
            x=dates, y=calls,
            name="Çağrı Sayısı",
            mode="lines+markers",
            line=dict(color="rgba(255, 127, 14, 1)", width=2),
            hovertemplate="<b>%{x}</b><br>%{y} çağrı<extra></extra>",
            secondary_y=True
        )
    )

    fig.update_xaxes(title_text="Tarih")
    fig.update_yaxes(title_text="Maliyet (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Çağrı Sayısı", secondary_y=True)

    fig.update_layout(
        title=f"📈 Maliyet Trendi ({days} Gün)",
        height=450,
        hovermode="x unified"
    )

    return fig
```

#### 3. Latency vs Cost (Scatter)

```python
def chart_latency_vs_cost(summary: CostSummary) -> go.Figure:
    """
    Scatter plot: Latency vs Maliyet (provider-bazlı).

    Bubble size: çağrı sayısı
    Renk: sağlık durumu (active=yeşil, error=kırmızı)
    """

    fig = go.Figure()

    # Provider-bazlı noktalar
    for p in summary.providers:
        if p.latency_ms is None:
            continue

        color_map = {
            "active": "green",
            "error": "red",
            "rate_limited": "orange",
            "unavailable": "gray"
        }
        color = color_map.get(p.health_status, "blue")

        fig.add_trace(go.Scatter(
            x=[p.latency_ms],
            y=[p.daily_cost_usd],
            mode="markers",
            name=p.provider,
            marker=dict(
                size=10 + (p.daily_calls / 100),  # Bubble size ∝ çağrı sayısı
                color=color,
                opacity=0.7,
                line=dict(width=1, color="white")
            ),
            text=[f"<b>{p.provider}</b><br>"
                  f"Latency: {p.latency_ms:.0f}ms<br>"
                  f"Günlük Maliyet: ${p.daily_cost_usd:.4f}<br>"
                  f"Çağrılar: {p.daily_calls}<br>"
                  f"Durum: {p.health_status}"],
            hovertemplate="%{text}<extra></extra>",
            showlegend=False
        ))

    fig.update_xaxes(title_text="Latency (ms)", type="log")
    fig.update_yaxes(title_text="Günlük Maliyet (USD)", type="log")

    fig.update_layout(
        title="⚡ Latency vs Maliyet (Provider-Bazlı)",
        height=500,
        hovermode="closest"
    )

    return fig
```

#### 4. Anomaly Flags (Bar Chart)

```python
def chart_anomaly_flags(summary: CostSummary) -> go.Figure:
    """
    Bar chart: Anomali sayacı (tip ve ciddiyete göre).
    """

    if not summary.anomalies:
        return go.Figure().add_annotation(
            text="✅ Anomali tespit edilmedi"
        )

    # Anomali gruplandırma
    anomaly_counts = {}
    for a in summary.anomalies:
        key = f"{a.flag_type} ({a.severity})"
        anomaly_counts[key] = anomaly_counts.get(key, 0) + 1

    labels = list(anomaly_counts.keys())
    values = list(anomaly_counts.values())
    colors_map = {
        "YUKSEK": "red",
        "ORTA": "orange",
        "DUSUK": "yellow"
    }
    colors = [
        colors_map.get(label.split("(")[1].rstrip(")"), "blue")
        for label in labels
    ]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(color=colors),
        text=values,
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Adet: %{y}<extra></extra>"
    )])

    fig.update_layout(
        title="⚠️ Anomali Flagler (Tip × Ciddiyete Göre)",
        xaxis_title="Anomali Tipi (Ciddiyet)",
        yaxis_title="Sayı",
        height=400,
        showlegend=False
    )

    return fig
```

#### 5. Cost Efficiency Heatmap (İsteğe Bağlı)

```python
def chart_cost_efficiency_grid(summary: CostSummary) -> go.Figure:
    """
    Heatmap: Provider × Metrik (Maliyet, Latency, Success Rate).
    """

    providers = [p.provider for p in summary.providers]

    metrics = {
        "Günlük Maliyet ($)": [p.daily_cost_usd for p in summary.providers],
        "Latency (ms)": [p.latency_ms or 0 for p in summary.providers],
        "Başarı Oranı (%)": [p.success_rate for p in summary.providers],
    }

    fig = go.Figure(data=go.Heatmap(
        z=list(metrics.values()),
        x=providers,
        y=list(metrics.keys()),
        colorscale="RdYlGn_r",
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>"
    ))

    fig.update_layout(
        title="📊 Provider × Metrik Heatmap",
        xaxis_title="Provider",
        yaxis_title="Metrik",
        height=400
    )

    return fig
```

---

### Veri Yükleme: load_cost_summary()

```python
import json
import streamlit as st
from pathlib import Path
from datetime import datetime, date

@st.cache_data(ttl=30)  # 30 saniye cache
def load_cost_summary() -> CostSummary:
    """
    optimizer_latest.json dosyasını oku ve CostSummary nesnesi oluştur.

    Fallback: Dosya yoksa veya parse hatası → boş CostSummary döndür
    """
    optimizer_file = Path("data/router/optimizer_latest.json")

    if not optimizer_file.exists():
        st.warning(f"⚠️ Optimizer dosyası bulunamadı: {optimizer_file}")
        return _empty_cost_summary()

    try:
        with open(optimizer_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"❌ JSON parse hatası: {e}")
        return _empty_cost_summary()

    # Maliyet verisi çıkarma
    usage_history = data.get("combo_istatistik", {}).get("usageHistory", {})
    request_details = data.get("combo_istatistik", {}).get("requestDetails", {})
    saglik = data.get("saglik", {})
    skorlar = data.get("skorlar", [])
    anomaliler_raw = data.get("anomaliler", [])

    total_cost = usage_history.get("toplam_maliyet_usd", 0.0)
    total_calls = sum(usage_history.get("provider_cagri_sayisi", {}).values())

    # Provider listesi oluşturma
    providers_dict = {p["provider"]: p for p in saglik.get("providerlar", [])}
    skor_dict = {s["provider"]: s for s in skorlar}

    providers = []
    for prov_name, prov_data in providers_dict.items():
        skor = skor_dict.get(prov_name, {})
        calls = usage_history.get("provider_cagri_sayisi", {}).get(prov_name, 0)
        cost = usage_history.get("provider_maliyet_toplam", {}).get(prov_name, 0.0)
        cost_per_call = usage_history.get("provider_maliyet_ort", {}).get(prov_name, 0.0)
        latency = request_details.get("provider_latency_ort", {}).get(prov_name)

        health = prov_data["durum"]
        status_map = {
            "active": "active",
            "error": "error",
            "unavailable": "rate_limited"
        }
        health_status = status_map.get(health.get("testStatus"), "unknown")

        success_calls = request_details.get("provider_status", {}).get(prov_name, {}).get("success", 0)
        error_calls = request_details.get("provider_status", {}).get(prov_name, {}).get("error", 0)
        total_prov_calls = success_calls + error_calls
        success_rate = (success_calls / total_prov_calls * 100) if total_prov_calls > 0 else 0

        provider_obj = ProviderCost(
            provider=prov_name,
            name=prov_data.get("name", prov_name),
            daily_cost_usd=cost,
            daily_calls=calls,
            daily_avg_cost_per_call=cost_per_call,
            monthly_cost_usd=cost * 30,
            monthly_calls=calls * 30,
            latency_ms=latency,
            success_rate=success_rate,
            error_rate=(100 - success_rate),
            health_status=health_status,
            backoff_level=health.get("backoffLevel") or 0,
            model_locks=health.get("modelLockSayisi") or 0,
            error_code=health.get("errorCode")
        )
        providers.append(provider_obj)

    # Anomali flagleme
    anomalies = []
    avg_cost = (total_cost / total_calls) if total_calls > 0 else 0

    for p in providers:
        # Yüksek maliyet anomalisi
        if p.daily_cost_usd > avg_cost * 2:
            anomalies.append(AnomalyFlag(
                provider=p.provider,
                name=p.name,
                flag_type="high_cost",
                severity="YUKSEK" if p.daily_cost_usd > avg_cost * 3 else "ORTA",
                message=f"Maliyet ortalamanın {p.daily_cost_usd/avg_cost:.1f}x'i",
                value=p.daily_cost_usd
            ))

        # Error anomalisi
        if p.error_code or p.health_status == "error":
            anomalies.append(AnomalyFlag(
                provider=p.provider,
                name=p.name,
                flag_type="error",
                severity="YUKSEK",
                message=f"Error {p.error_code}" if p.error_code else "Test hatası",
                value=p.error_code or 0
            ))

        # Rate limit anomalisi
        if p.backoff_level >= 5:
            anomalies.append(AnomalyFlag(
                provider=p.provider,
                name=p.name,
                flag_type="rate_limited",
                severity="ORTA",
                message=f"Backoff level {p.backoff_level}",
                value=p.backoff_level
            ))

        # Latency anomalisi
        if p.latency_ms and p.latency_ms > 5000:
            anomalies.append(AnomalyFlag(
                provider=p.provider,
                name=p.name,
                flag_type="latency",
                severity="DUSUK",
                message=f"Yüksek latency {p.latency_ms:.0f}ms",
                value=p.latency_ms
            ))

    # Trend oluşturma (şimdilik dummy — gerçekte multiple JSON'dan oluşturulacak)
    trend_7d = [
        TrendPoint(
            date=date.today(),
            cost_usd=total_cost,
            calls=total_calls,
            avg_cost_per_call=avg_cost,
            anomalies_count=len([a for a in anomalies if a.severity == "YUKSEK"])
        )
    ]

    return CostSummary(
        timestamp=data.get("timestamp", datetime.now().isoformat()),
        generated_at=datetime.now().isoformat(),
        total_cost_today_usd=total_cost,
        total_calls_today=total_calls,
        total_avg_cost_today=avg_cost,
        total_cost_month_usd=total_cost * 30,
        total_calls_month=total_calls * 30,
        providers=providers,
        anomalies=anomalies,
        trend_7d=trend_7d,
        trend_30d=trend_7d,  # TODO: Gerçek trend verisi
        optimizer_file=str(optimizer_file),
        cache_ttl=30
    )

def _empty_cost_summary() -> CostSummary:
    """Boş CostSummary (fallback)."""
    return CostSummary(
        timestamp=datetime.now().isoformat(),
        generated_at=datetime.now().isoformat(),
        total_cost_today_usd=0.0,
        total_calls_today=0,
        total_avg_cost_today=0.0,
        total_cost_month_usd=0.0,
        total_calls_month=0,
        providers=[],
        anomalies=[],
        trend_7d=[],
        trend_30d=[],
        optimizer_file="",
        cache_ttl=30
    )
```

---

### render_cost_tab() — Streamlit UI

```python
def render_cost_tab() -> None:
    """
    Admin Panel Tab 10: 💰 AI Maliyet sekmesi.

    Gösterge:
    1. KPI kartları (günlük/aylık maliyet, çağrı sayısı)
    2. Provider breakdown (pie chart)
    3. Maliyet trendi (line chart + dual axis)
    4. Latency vs Cost (scatter)
    5. Anomali flagler (bar chart)
    6. Provider detay tablosu
    7. Uyarılar (yüksek maliyet, hatalar)
    """
    st.subheader("💰 AI Cost Dashboard")

    # Veri yükleme
    summary = load_cost_summary()

    if not summary.providers:
        st.warning("⚠️ Maliyet verisi yüklenemedi. Optimizer çalıştırılmış mı?")
        return

    # --- KPI Kartları ---
    st.subheader("📊 Özet Metrikler")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "💰 Günlük Maliyet",
            f"${summary.total_cost_today_usd:.2f}",
            delta=f"${summary.total_cost_month_usd:.2f}" if summary.total_cost_month_usd > 0 else None,
            delta_color="off"
        )

    with col2:
        st.metric(
            "📞 Günlük Çağrı",
            f"{summary.total_calls_today:,}",
            delta=f"{summary.total_calls_month:,}/ay",
            delta_color="off"
        )

    with col3:
        avg = summary.total_avg_cost_today
        st.metric(
            "💵 Ort. Çağrı Maliyeti",
            f"${avg:.6f}",
            delta=None,
            delta_color="off"
        )

    with col4:
        st.metric(
            "📅 Aylık Tahmin",
            f"${summary.total_cost_month_usd:.2f}",
            delta=f"+${(summary.total_cost_month_usd - summary.total_cost_today_usd):.2f}",
            delta_color="inverse"
        )

    with col5:
        anomaly_count = len(summary.anomalies)
        st.metric(
            "⚠️ Anomaliler",
            anomaly_count,
            delta=f"{len([a for a in summary.anomalies if a.severity == 'YUKSEK'])} kritik",
            delta_color="inverse" if anomaly_count > 0 else "off"
        )

    st.divider()

    # --- Charts (3 sütun, 2 satır) ---
    st.subheader("📈 Görselleştirmeler")

    # Satır 1
    col1, col2 = st.columns(2)

    with col1:
        fig_pie = chart_provider_breakdown(summary)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_trend = chart_daily_trend(summary, days=7)
        st.plotly_chart(fig_trend, use_container_width=True)

    # Satır 2
    col1, col2 = st.columns(2)

    with col1:
        fig_scatter = chart_latency_vs_cost(summary)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        fig_anomaly = chart_anomaly_flags(summary)
        st.plotly_chart(fig_anomaly, use_container_width=True)

    st.divider()

    # --- Provider Detay Tablosu ---
    st.subheader("🔧 Provider Detayı")

    provider_rows = []
    for p in sorted(summary.providers, key=lambda x: x.daily_cost_usd, reverse=True):
        provider_rows.append({
            "Provider": p.provider,
            "İsim": p.name,
            "Günlük ($)": f"${p.daily_cost_usd:.4f}",
            "Aylık ($)": f"${p.monthly_cost_usd:.4f}",
            "Çağrılar": f"{p.daily_calls:,}",
            "$/Çağrı": f"${p.daily_avg_cost_per_call:.6f}",
            "Latency (ms)": f"{p.latency_ms:.0f}" if p.latency_ms else "—",
            "Başarı (%)": f"{p.success_rate:.1f}%",
            "Durum": "✅" if p.health_status == "active" else f"❌ {p.health_status}",
        })

    provider_df = pd.DataFrame(provider_rows)
    st.dataframe(provider_df, use_container_width=True, hide_index=True)

    st.divider()

    # --- Anomaliler ---
    if summary.anomalies:
        st.subheader("⚠️ Tespit Edilen Anomaliler")

        anomaly_rows = []
        for a in sorted(summary.anomalies, key=lambda x: ("YUKSEK", "ORTA", "DUSUK").index(x.severity)):
            severity_icon = "🔴" if a.severity == "YUKSEK" else "🟠" if a.severity == "ORTA" else "🟡"
            anomaly_rows.append({
                "Ciddiyet": f"{severity_icon} {a.severity}",
                "Provider": a.provider,
                "Tip": a.flag_type,
                "Mesaj": a.message,
                "Değer": f"{a.value:.2f}",
            })

        anomaly_df = pd.DataFrame(anomaly_rows)
        st.dataframe(anomaly_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Anomali tespit edilmedi — sistem temiz!")

    st.divider()

    # --- Meta Bilgi ---
    st.subheader("ℹ️ Bilgi")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"📁 Kaynak: {summary.optimizer_file}")
    with col2:
        st.caption(f"🕐 Güncelleme: {summary.generated_at[:19]}")
    with col3:
        st.caption(f"⏱️ Cache TTL: {summary.cache_ttl}s")
```

---

## 🔗 Entegrasyon Noktaları

### 1. app.py — Tab 10 Ekleme

**Dosya:** [`app.py`](../../app.py)

**Değişiklik (satır ~413):**

```python
# Mevcut:
admin_tab1, ..., admin_tab9 = st.tabs([...])

# Yeni:
admin_tab1, ..., admin_tab9, admin_tab10 = st.tabs([
    "📊 Sistem Durumu",
    "🔑 API Yönetimi",
    "📋 Webhook Metrikleri",
    "📋 Karar Defteri",
    "👥 Kullanıcı Yönetimi",
    "📈 KPI Kartları",
    "🔌 Webhook Monitor",
    "🔍 Denetim",
    "⏱️ Performans",
    "💰 AI Maliyet"  # YENİ
])

# Yeni tab içeriği
with admin_tab10:
    from web_dashboard.tabs.admin_cost import render_cost_tab
    render_cost_tab()
```

### 2. admin_kpi.py — Maliyet Metric Ekleme

**Dosya:** [`web_dashboard/tabs/admin_kpi.py`](../../web_dashboard/tabs/admin_kpi.py)

**Eklenecek Fonksiyon:**

```python
@st.cache_data(ttl=60)
def load_cost_metrics() -> dict[str, Any]:
    """9Router optimizer'dan maliyet metriği yükle."""
    try:
        from web_dashboard.tabs.admin_cost import load_cost_summary
        summary = load_cost_summary()
        return {
            "daily_cost": summary.total_cost_today_usd,
            "monthly_cost": summary.total_cost_month_usd,
            "calls": summary.total_calls_today,
        }
    except Exception:
        return {"daily_cost": 0, "monthly_cost": 0, "calls": 0}
```

**KPI Tab'ında Eklenecek (yaklaşık satır 300 civarı):**

```python
# Maliyet kartları
st.subheader("💰 AI Cost Özeti")
cost = load_cost_metrics()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Günlük Maliyet", f"${cost['daily_cost']:.2f}")
with col2:
    st.metric("Aylık Tahmin", f"${cost['monthly_cost']:.2f}")
with col3:
    st.metric("Günlük Çağrı", f"{cost['calls']:,}")

# "Detaylar için 💰 AI Maliyet sekmesine tıklayın" notu
st.caption("👉 Detaylı analiz için Admin Panel'deki **💰 AI Maliyet** sekmesini kullanın")
```

### 3. admin_performance.py — Dolar/Çağrı Metric Ekleme

**Dosya:** [`web_dashboard/tabs/admin_performance.py`](../../web_dashboard/tabs/admin_performance.py)

**Eklenecek (satır ~150 sonrası):**

```python
# --- AI Cost Efficiency ---
st.divider()
st.subheader("💰 AI Cost Efficiency")

from web_dashboard.tabs.admin_cost import load_cost_summary
try:
    cost_summary = load_cost_summary()

    col1, col2 = st.columns(2)
    with col1:
        avg_cost = cost_summary.total_avg_cost_today
        calls_per_dollar = (1.0 / avg_cost) if avg_cost > 0 else 0
        st.metric(
            "Dolar Başına Çağrı",
            f"{calls_per_dollar:.0f}",
            help="Kaç API çağrısı 1 dolar'a denk gelmektedir"
        )

    with col2:
        daily_cost = cost_summary.total_cost_today_usd
        st.metric(
            "Günlük AI Maliyeti",
            f"${daily_cost:.2f}",
            help="Son 24 saat optimizer verisi"
        )
except Exception:
    st.warning("AI Cost metrikleri yüklenemedi")
```

---

## 📋 Implementasyon Görev Listesi

### Faz 1: Çekirdek Modül (admin_cost.py)
- [ ] `admin_cost.py` dosyası oluştur
- [ ] Dataclass'lar tanımla (ProviderCost, CostSummary, AnomalyFlag, TrendPoint)
- [ ] `load_cost_summary()` fonksiyonu yaz
- [ ] `_empty_cost_summary()` fallback yaz

### Faz 2: Plotly Charts
- [ ] `chart_provider_breakdown()` yaz
- [ ] `chart_daily_trend()` yaz
- [ ] `chart_latency_vs_cost()` yaz
- [ ] `chart_anomaly_flags()` yaz
- [ ] `chart_cost_efficiency_grid()` (optional) yaz

### Faz 3: Streamlit UI
- [ ] `render_cost_tab()` fonksiyonu yaz
- [ ] KPI kartları implementasyonu
- [ ] Chart entegrasyonu
- [ ] Provider detay tablosu
- [ ] Anomali gösterimi

### Faz 4: app.py Entegrasyonu
- [ ] Tab 10 ekle (admin_tab10)
- [ ] Import'ları düzenle (`from web_dashboard.tabs.admin_cost import render_cost_tab`)
- [ ] Tab with bloğu ve render çağrısı

### Faz 5: İlişkili Sekmeler Güncellemesi
- [ ] admin_kpi.py — Maliyet metric ekleme
- [ ] admin_performance.py — Dolar/çağrı metric ekleme

### Faz 6: Test & Doğrulama
- [ ] Optimizer çıktısı kontrol (optimizer_latest.json var mı?)
- [ ] Cache behavior test (TTL=30s)
- [ ] Chart renderinge test
- [ ] Anomali tespiti doğrulaması
- [ ] Tab navigation test

---

## 🎯 Teknik Sınırlar

✅ **Yapılacak:**
- Batch read optimizer_latest.json (real-time DB değil)
- TTL=30s cache (Streamlit)
- Plotly + fallback (st.bar_chart)
- Provider-bazlı anomali (backoff ≥5, cost 2x ortalaması)
- Günlük/aylık trend (basit 30x ekstrapol)

❌ **YAPILMAYACAK:**
- Real-time 9Router DB polling
- ML forecasting / trend prediction
- Per-model breakdown (provider-level yeterli)
- Webhook entegrasyonu

---

## 📝 Notlar

1. **Trend Verisi:** Şu an single-day trend (optimizer_latest.json). Gerçek 7/30 gün trend için multiple JSON'lar arşivlenmelidir (`data/router/optimizer_YYYYMMDD_HHMM.md` → parse et)

2. **Anomali Eşikleri:**
   - Maliyet anomali: `daily_cost > avg_cost * 2`
   - Backoff anomali: `backoff_level >= 5`
   - Latency anomali: `latency_ms > 5000`

3. **Cache TTL:** Streamlit @st.cache_data(ttl=30) — optimizer dosyası ne kadar sıklıkta güncelleniyor?

4. **Fallback Stratejisi:** Optimizer dosyası yoksa/parse hata → boş CostSummary (UI crash değil)

5. **Türkçe İçerik:** Tüm başlıklar, metrikler ve uyarılar Türkçe

---

## 🔄 Sonraki Adımlar

1. **Mimarinin onaylanması** ✅
2. **admin_cost.py implementasyonu** → Code mode'a geç
3. **app.py entegrasyonu** → Code mode
4. **Test & doğrulama** → Debug mode
5. **Trend verisi iyileştirmesi** (future: gerçek zaman serisi)

---

**Versiyon:** V1 — Mimari Tasarım
**Statü:** 🏗️ Ready for Implementation
**Sonraki:** Code Mode → admin_cost.py yazılması
