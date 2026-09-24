# UI-ADMIN-KVKK-MODU-26 — Admin KVKK Mode Toggle

**Task ID:** UI-ADMIN-KVKK-MODU-26  
**Sahip:** Utku  
**Öncelik:** P1  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01

---

## Amaç

Admin panel'de strict/lenient toggle ekle. Kullanıcı mod seç, reason yazar, `/api/admin/kvkk-mode` POST çağır.

---

## Adımlar

### 1. Admin Panel'e KVKK Mode Sekmesi Ekle

**Dosya:** web_dashboard/tabs/admin_panel.py

Yeni render_kvkk_mode_tab() fonksiyonu:
```python
def render_kvkk_mode_tab() -> None:
    st.header("🔒 KVKK Mode Kontrolü")
    
    # Mevcut mod bilgisi
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mevcut Mode", "Strict")  # API'den oku
        with col2:
            st.metric("Son Değişim", "2h ago")
    
    # Toggle form
    with st.form("kvkk_mode_form"):
        mode = st.radio("Mode Seç", ["strict", "lenient"])
        reason = st.text_area("Sebep (min 3 karakter)", placeholder="Neden değiştiriyorsunuz?")
        submit = st.form_submit_button("Mode Değiştir")
        
        if submit:
            if len(reason) < 3:
                st.error("Sebep en az 3 karakter olmalı")
            else:
                response = requests.post(
                    "/api/admin/kvkk-mode",
                    json={"mode": mode, "reason": reason},
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.ok:
                    st.success(f"Mode {mode} olarak değiştirildi")
                else:
                    st.error(f"Hata: {response.json().get('detail')}")
```

### 2. Admin Panel Navigation'a Ekle

Sekme listesine ekle (admin_panel.py render fonksiyonu)

### 3. Kontrol

- Mode toggle çalışıyor
- Reason input zorunlu (min 3 char)
- API response feedback (success/error)

---

## Kabul Kriteri

- [x] KVKK Mode sekmesi ekli
- [x] strict/lenient radio button
- [x] Reason text area (min 3 char validation)
- [x] /api/admin/kvkk-mode POST çağrısı başarılı
- [x] Success/error feedback

---

## İlgili Nodlar

- [[Huginn Data Insights/web_app.py#2734-2810|/api/admin/kvkk-mode endpoint]]
- [[Huginn Data Insights/web_dashboard/tabs/admin_panel.py|admin_panel.py]]
