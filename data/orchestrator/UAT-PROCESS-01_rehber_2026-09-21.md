# UAT — Kullanıcı Kabul Süreci (User Acceptance Testing)

**Karar:** [[D-66]] [[D-67]] [[D-77]] Orkestratör + Sahip + Ürün Sahibi

**Tarih:** 2026-09-21  
**Hazırlayan:** Orkestratör (İhsan)  
**Rapor Sahibi:** Ürün Sahibi  
**Dönem:** Günlük izleme → Haftalık sprint toplantısı

---

## 1. Amaç

Özellikle **dashboard UI/UX görevleri** (DASH-*) ve **müşteri paneli** (COP-*) için:
- Günlük kullanıcı geri bildirimini sistemli topla
- Haftalık sprint toplantısında ürün sahibine rapor sun
- Tasarım + uygulama + kullanıcı kabul arasında geri beslemesi kapat

---

## 2. Günlük Akış (Daily)

### 2.1 Sahip Görevi
**Kime:** Ürün Sahibi (Admin Dashboard sorumlusu)  
**Ne zaman:** Görev tesliminden **24-48 saat sonra**  
**İçerik:**

1. **Fonksiyonel test (5 min):**
   - Temel akış çalışıyor mu? (liste yükleme, filtre, sayfalama)
   - Hata var mı? (konsol, eksik alan, broken link)
   - Performans uygun mu? (sayfa yükleme <3s)

2. **UX kontrol (10 min):**
   - Arayüz tutarlı mı? (renkler, yazı, boşluk)
   - Navigasyon anlaşılır mı? (butonlar, ikonlar)
   - Erişilebilirlik sorun var mı? (dark mode, zoom, screen reader)

3. **Rapor formatı:** `data/orchestrator/UAT-<TASK_ID>-<TARIH>-<SAHIP>.txt`

   ```
   Task: DASH-UX-02b
   Test Tarihi: 2026-09-21 14:30
   Sahip: Utku
   
   ✅ Fonksiyonel:
   - Sekmeler yükleniyor
   - Veri akışı OK
   
   ⚠️ UX:
   - Filtre düğmesi çok dar (hover etmek zor)
   - Mobil görünümde başlık kesiyor
   
   ❌ Blokaj:
   - Bağımlı görev COP-25 henüz tamamlanmadı
   
   Onay: [Ürün Sahibi Ad] ✅ / ⏳ / ❌
   ```

### 2.2 Orkestratör Görevi
**Kime:** Teslim alındığında  
**Ne zaman:** Günlük (öğle / iş sonu)  
**İçerik:**

1. UAT raporlarını topla
2. Blokajları tespit et (görev dışı vb.)
3. Ürün Sahibine özet bildir (Slack/email)

---

## 3. Haftalık Sprint Toplantısı (Weekly)

### 3.1 Rapor Sunumu
**Ne zaman:** Cuma 10:00 (Sprint sonu)  
**Sunan:** Ürün Sahibi  
**Katılımcılar:** Ürün Sahibi + Orkestratör + Ajans Lead

**Agenda (20 min):**

1. **UAT Özeti (5 min)**
   - Bu hafta test edilen görevler (kaç tane, hangileri)
   - Genel onay oranı (% ✅ / ⏳ / ❌)

2. **Bulgular (10 min)**
   - Tekrarlanan sorunlar (ex: mobil görünüm, erişilebilirlik)
   - Yüksek öncelikli geri bildirimler
   - Tasarım çelişkileri (mockup vs uygulama)

3. **Aksiyon Maddeler (5 min)**
   - Yeni görevler veya düzeltme listesi (hotfix / sonraki sprint)
   - Sorunlu tasarımlara "D-77 devrediş" veya "tekrar tasarım"

---

## 4. UAT Durumlar

```
✅ Onaylandı
   → Sahip test geçti, ürün sahibi onay verdi
   → Görev "done" işaretlenir

⏳ Şartlı Onay (Minor Fix)
   → Küçük UX düzeltme gerekli (ex: renk, yazı boyutu)
   → 1–2 gün içinde düzeltme
   → Sonra tekrar test

❌ Reddedildi (Major Rework)
   → Temel tasarım sorunu
   → "tekrar tasarım" görev açıl (D-77 devrediş)
   → Özgün görev "blocked" kalır
```

---

## 5. Haftalık UAT Raporu Şablonu

**Dosya:** `data/orchestrator/UAT-HAFTALIK-RAPOR_<TARIH>_<SAHIBI>.md`

```markdown
# Haftalık UAT Raporu — [Hafta Tarihi]

## Özet
- Sınanan görevler: 5 (DASH-UX-02b, COP-26, ...)
- Onay oranı: ✅ 60% / ⏳ 30% / ❌ 10%

## Görev Başlığı Bazında

### DASH-UX-02b (Sekmeler)
- **Test Tarihi:** 2026-09-21
- **Sahip:** Utku
- **Durum:** ✅ Onaylandı
- **Bulgu:** Mobil görünümde başlık kesiyor (minor)
- **Aksiyon:** Responsive padding düzeltildi

### COP-26 (Müşteri Paneli)
- **Test Tarihi:** 2026-09-22
- **Sahip:** İhsan
- **Durum:** ⏳ Şartlı Onay
- **Bulgu:** 
  - Filtre UI tutarsız (design vs code)
  - Bildirim feed simgeesi kalabalık
- **Aksiyon:** Yeni görev açıl (UAT-MINOR-COP-26-FILTRE)

## Tekrarlanan Sorunlar (Bu Hafta)
1. **Mobil Responsive:** Sidebar genişliği %15 görevde sorun
2. **Erişilebilirlik:** Renk kontrastı WCAG AA'ya uymuyor

## Sonraki Sprint Tavsiyesi
- Responsive tasarım "D-77 devrediş" olarak yeniden yapılsın (Copilot)
- Erişilebilirlik denetim aracı (axe DevTools) CI'ye eklenmesi

## Imza
Ürün Sahibi: ___________  
Tarih: ___________
```

---

## 6. Entegrasyon: Sprint Döngüsü

```
PAZARTESİ (Sprint Başla)
  └─ D-72 Sprint Başlangıç Tablosu (Orkestratör)

SALŞ–CUMA (İş Günleri)
  ├─ Ajans: Görev yazıyor + test ediyor
  ├─ Sahip: UAT raporu veriyor (günlük)
  └─ Orkestratör: UAT topluyor

CUMA (Sprint Sonu)
  ├─ 10:00 Sprint Toplantısı (UAT Raporu sunumu)
  ├─ D-67 Haftalık Özeleştiri (Orkestratör, D-67 formatı)
  └─ D-72 Sonraki Sprint Planlama
```

---

## 7. Dosya Adlandırma (D-183)

- **Günlük UAT:** `UAT-<TASK_ID>-<ISO_TARIH>-<SAHIP>.txt`
  - Örn: `UAT-DASH-UX-02b-2026-09-21-utku.txt`

- **Haftalık Rapor:** `UAT-HAFTALIK-RAPOR_<ISO_TARIH>_<ÜRÜN_SAHİBİ_KISA>.md`
  - Örn: `UAT-HAFTALIK-RAPOR_2026-09-21_admin.md`

---

## 8. Wikilink (D-184)

[[D-55]] — Rapor 5 başlık (günlük + haftalık)  
[[D-66]] — Brifsiz atama yasağı (UAT de sıfırdan başlama riski)  
[[D-67]] — Haftalık özeleştiri (UAT bulguları dahil)  
[[D-72]] — Sprint başlangıç (UAT planarı input)  
[[D-77]] — Pano işleri (UAT rejection → devrediş)  
[[D-183]] — Dosya adlandırma kuralı  
[[D-184]] — Graph köprü (UAT raporu ↔ görev)
