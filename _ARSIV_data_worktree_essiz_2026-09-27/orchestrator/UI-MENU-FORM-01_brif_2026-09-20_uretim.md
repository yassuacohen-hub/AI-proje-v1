# Brief: UI-MENU-FORM-01 — Kullanıcı Menü Sayfasına Form Entegrasyonu

**Görev ID:** UI-MENU-FORM-01  
**Sahip:** UTKU (Üretim/Hacim)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `web_dashboard/pages/menu.py`, `src/company_master/ui/forms/menu_form.py`

---

## DURUM
Zincir başlangıcı. Önceki görev yok; hemen tetiklenir.

---

## AMAÇ
Admin panelinde **Kullanıcı Menü Yönetimi** sayfasına form ekle:
- Menü öğelerini (başlık, link, ikon) düzenle
- Sıralama drag-drop (Streamlit widgetleri ile basit)
- Kaydet & İptal butonları
- Form doğrulama (başlık boş olmasın, link valid URL olmalı)

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Form Bileşenleri
- Menü adı (text input) — boş bırakılamaz
- Menü linki (text input) — `/` ile başlamalı
- İkon seçimi (selectbox) — kanonik liste
- Aktif toggle (checkbox)
- Sıra (number_input, 1-100 arası)

### 2. Validasyon
- Başlık boşsa: inline error "Başlık zorunlu"
- Link `/` ile başlamazsa: "Link / ile başlamalı"
- Duplicate menü adı: "Bu ad zaten var"

### 3. CRUD İşlemleri
- Yeni ekle (Add button)
- Varsa güncelle (Edit button)
- Sil (Delete with confirmation)
- Kaydet (Save all — DB'ye yaz)

### 4. Arayüz Şeması
- Sidebar: Menü listesi (expandable)
- Main: Form (seçili menü göster)
- Footer: Kaydet / İptal butonları
- Renk şeması: Muninn brand (Indigo #6366f1)

### 5. Erişilebilirlik
- Form label'ları var (aria-label)
- Hata mesajları Screen Reader oku
- Keyboard navigation (Tab + Enter)

### 6. Test Dosyası
- `tests/test_menu_form.py` — 5 test
  - Form oluşturma (`test_menu_form_olustur`)
  - Validasyon (`test_menu_form_validasyon`)
  - CRUD işlemleri (`test_menu_form_crud`)
- Tüm testler yeşil olmalı: `python -X utf8 -m pytest tests/test_menu_form.py -v`

---

## DOSYALAR
- Yaz: `web_dashboard/pages/menu.py`
- Yaz: `src/company_master/ui/forms/menu_form.py`
- Düzenle: `tests/test_menu_form.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ Form bileşenleri tam  
✅ Validasyon hepsi çalışıyor  
✅ CRUD (Create/Read/Update/Delete) operasyonel  
✅ Test sayısı: 5 (tümü yeşil)  
✅ UTF-8 temiz, BOM yok, Türkçe karakterler doğru  

---

## SONRAKI GÖREV
UI-FORM-VALIDATION-02 (zincir otomatik tetiklenir)
