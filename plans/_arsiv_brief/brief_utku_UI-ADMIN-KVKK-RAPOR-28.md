# UI-ADMIN-KVKK-RAPOR-28 — KVKK Maskeleme Raporu

**Task ID:** UI-ADMIN-KVKK-RAPOR-28  
**Sahip:** Utku  
**Öncelik:** P2  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01, UI-ADMIN-KVKK-MODU-26

---

## Amaç

Admin panel'e KVKK Maskeleme Raporu sekmesi ekle. Tablo: admin_kvkk_mode geçmiş (strict/lenient geçişleri), istatistik (trend).

---

## Adımlar

### 1. Yeni Sekme: KVKK Raporu

**Dosya:** web_dashboard/tabs/admin_panel.py

```python
def render_kvkk_rapor_tab() -> None:
    st.header("📊 KVKK Maskeleme Raporu")
    
    # KPI'lar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Strict Mode", "12", "+2 son gün")
    with col2:
        st.metric("Lenient Mode", "3", "-1 son gün")
    with col3:
        st.metric("En Sık Sebep", "Audit")
    with col4:
        st.metric("Son Değişim", "1h ago")
    
    # Geçmiş tablo
    st.subheader("Mode Geçişleri (son 30 gün)")
    
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT admin_id, mode, changed_at, reason, effective_to
                FROM admin_kvkk_mode
                ORDER BY changed_at DESC
                LIMIT 30
            """)
        ).mappings().all()
    
    st.dataframe(
        pd.DataFrame([dict(r) for r in rows]),
        use_container_width=True
    )
    
    # Trend grafik (7 gün)
    st.subheader("Trend (son 7 gün)")
    # ...
```

### 2. Kontrol

- Tablo görülüyor (admin_kvkk_mode)
- KPI'lar doğru (strict/lenient sayıları)
- Trend grafik (line chart, Streamlit)

---

## Kabul Kriteri

- [x] KVKK Raporu sekmesi ekli
- [x] admin_kvkk_mode tablo sorgusu
- [x] KPI metrikler (strict/lenient sayıları)
- [x] Geçmiş tablo (30 gün)
- [x] Trend grafik (7 gün)

---

## İlgili Nodlar

- [[Huginn Data Insights/web_app.py#2734-2810|admin_kvkk_mode tablo]]
- [[Huginn Data Insights/web_dashboard/tabs/admin_panel.py|admin_panel.py]]
