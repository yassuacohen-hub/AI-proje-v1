# UI-KONTROL-PANOSU-32 — Admin Kontrol Panosu

**Task ID:** UI-KONTROL-PANOSU-32  
**Sahip:** Utku  
**Öncelik:** P2  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01, UI-ADMIN-KVKK-MODU-26

---

## Amaç

Admin Panel'e Kontrol Panosu sekmesi ekle. Metrikler: maskeli alanlar (strict), açık alanlar (lenient), tier dağılımı, günlük trend.

---

## Adımlar

### 1. Sekmesi Ekle: Kontrol Panosu

**Dosya:** web_dashboard/tabs/admin_panel.py

```python
def render_kontrol_panosu_tab() -> None:
    st.header("📈 Kontrol Panosu")
    
    # KPI Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Maskeli Alan", "8/33", "+2 son gün")  # strict mode
    with col2:
        st.metric("Açık Alan", "25/33", "-1 son gün")  # lenient mode
    with col3:
        st.metric("Terminal User", "47", "↑ 5%")
    with col4:
        st.metric("Enterprise User", "12", "↓ 2%")
    
    # Tier Dağılımı (bar chart)
    st.subheader("User Dağılımı (Tier)")
    tier_data = {
        "Terminal": 47,
        "Strategic": 23,
        "Enterprise": 12
    }
    st.bar_chart(tier_data)
    
    # Günlük Trend (7 gün, line chart)
    st.subheader("Trend (son 7 gün)")
    # ... line chart ...
    
    # Mode Geçişleri (mini tablo)
    st.subheader("Son Mode Geçişleri")
    # ... dataframe ...
```

### 2. Kontrol

- KPI'lar görülüyor (maskeli/açık alan sayıları)
- Tier bar chart
- 7 gün trend (line)
- Mode geçişleri tablo

---

## Kabul Kriteri

- [x] Kontrol Panosu sekmesi ekli
- [x] KPI metrikler (maskeli/açık/tier dağılımı)
- [x] Tier bar chart
- [x] 7 gün trend line chart
- [x] Mode geçişleri mini tablo

---

## İlgili Nodlar

- [[Huginn Data Insights/web_dashboard/tabs/admin_panel.py|admin_panel.py]]
