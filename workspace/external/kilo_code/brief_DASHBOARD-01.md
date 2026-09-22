[[Huginn Data Insights/workspace/external/claude_code/brief_DASHBOARD-01.md]]

# Dashboard İyileştirme — Kullanıcı Deneyimi Brief'i

**Ajan:** Kilo Code  
**Odak:** UX, tema, modal yapı, responsive tasarım  
**Tarih:** 2026-09-12

---

## Mevcut Durum

- **Dashboard:** Streamlit + HTML hybrid, `web_dashboard/index.html` (24KB), `app.js` (97KB)
- **KPI:** 14.000 firma, NACE dağılımı, kalite skoru, kaynak dağılımı
- **Eksikler:**
  - Firma detay modal yok (sadece liste)
  - Filtreler sadece API'de, UI'da yok
  - Tema değişimi yok (sadece açık tema)
  - Yükleme göstergeleri yok
  - Toast bildirimleri yok
  - Sayfalama yok (14K firma bir anda yükleniyor)

## Mevcut Öneriler

| ID | Görev | Kullanıcı Etkisi |
|----|-------|-----------------|
| UX-1 | Modal Yapı | Firma detay, filtre, admin için popup pencereler |
| UX-2 | Responsive Tasarım | Mobil/tablet uyumluluk |
| UX-3 | Dark/Light Tema | Göz konforu, kişiselleştirme |
| UX-4 | Yükleme İkonları | Veri yüklenirken feedback |
| UX-5 | Toast Bildirimleri | İşlem sonucu bilgilendirme |
| UX-6 | Sayfalama | 14K firma için hızlı erişim |
| T-1 | Modern Tema | Glassmorphism, gradient'ler |
| T-2 | Minimalist Tema | Sade, hızlı |
| T-3 | Karanlık Tema | Dark mode |
| T-4 | Aydınlık Tema | Light mode |
| T-5 | Özelleştirilebilir | Kullanıcı renk/font seçimi |

## Senden İsteniyor

1. Bu planı **kullanıcı deneyimi açısından** değerlendir
2. Hangi UX özelliğinin **en çok etki yaptığını** sırala
3. **Tema stratejisi** öner (hangi tema? nasıl uygulanır?)
4. **Modal mimarisi** nasıl olur? (tek modal mı? çoklu mı?)
5. **Responsive breakpoint'leri** öner
6. **Yeni UX fikirleri** ekle (animasyon, micro-interaction vb.)

## Kilo Code — UX Önerileri

### Öncelik Sıralaması (UX Etkiye Göre)
1. **Açık/Koyu Tema Değiştirici** — Kullanıcı tercihini kaydeder; gece/toplu kullanım için en hızlı etki.
2. **Hızlı Firma Detay Modalı** — Sağ panel yerine kompakt modal; mobilde "Kimler Uygun/Kopyala" için tek tık erişim.
3. **Çoklu Kaynak Filtre Çipleri** — Seçilen kaynaklar chip olarak gösterilir, tek tek iptal edilebilir; API'deki `sources=` virgüllü parametresi korunur.
4. **Yazdır/Dışa Aktarılabilir Rapor** — KPI + tablo bölümlerini PDF/HTML olarak dışa aktar; satış toplantıları için kritik.
5. **Kısayol Masası (Ctrl+K açılır)** — Mevcut Ctrl+K aramasının yanına erişilebilir kısayol listesi; yeni kullanıcı öğrenmesi için.
6. **Mobil Tablo Kart Görünümü** — 760px altı satırların bir kısmı gizlendiği için hücresi başlı kullanıcı kartı görüntüsüne geçmelidir.
7. **Eşleştirme Sonuç Geçiş Animasyonları** — Skor barları ve listeler için yumuşak height/opacity geçişleri; veri değişimini hissettirir.
8. **Tanımlanabilir Yüklenme Durumu** — Mevcut skeleton + toast eksiği: global "yükleniyor" bantı ve per-section ilerleme yüzdesi.

### Tema Stratejisi
- **Tema:** Sistem temasına göre başlayan iki tonlu (Dark/Light) CSS değişkenleri.
- **Uygulama:** `:root` ve `[data-theme="light"]` ikisi de CSS değişkenlerini tanımlar; `localStorage` + `matchMedia('prefers-color-scheme')` kilidi.
- **Dosyalar:** `web_dashboard/css/style.css` (değişkenler), `web_dashboard/index.html` (theme toggle butonu — `#theme-toggle`), `web_dashboard/js/app.js` (`applyTheme`/`applyThemeToggle`).

### Modal Mimari
- **Yapı:** Tek yeniden kullanılabilir sabit modal component; `buildModal({title, body, actions, onClose})`.
- **Kullanım:** Üyelik başvurusu, hızlı firma detayı, admin onay paneli için aynı altyapı. `buildMembershipModal` ve `_openTasksAdmin` bu componente revize edilir.
- **Faydası:** Overlay sayısı azalır, focus yönetimi ve Escape kapatma standartlaşır.

### Responsive Breakpoints
- **Mobile:** `< 760px` — hamburger menü, alt bilgi çubuğu gizli, tablo yatay kaydırılabilir, kompakt kart liste.
- **Tablet:** `760px – 1150px` — detay paneli sağ üstte küçük modal olarak açılır; KPI 2×2.
- **Desktop:** `> 1150px` — tam 3 bölümlü kaplama (sidebar + içerik + detay paneli).
- **Ek:** `1400px` üstü KPI 2×2 ve grafik tek sütun; `1250px` üstü üst bilgi kısayol gizlenir.

### Ek UX Fikirler
- **Kısa İşlem Geri Bildirimi:** İşlem sonuçları (kopyalama, oy ekleme, onay) için Toast'un yanına 2 saniyelik mini ikon + check/× rengi.
- **Kaydırma Kilidi:** Detay paneli açılırken arka plan karartma + scroll kilidi zaten mevcut; Escape'ten sonra önceki odak geri döner (mevcut `drawerReturnFocus`).
- **Uzaktaki Bilgi Notları:** Mevcut tooltip sistemi 210px max-width; firmalar listesinde hücre tooltip'leri 60px civarındaydı, 240px'e çıkarılmalı.
- **Tema Otomatik Senkronizasyonu:** Linux/güncel temasının değişmesi durumunda otomatik tespit ve uyarı.

### Riskler
- **Tema geçişi:** Hızlı tema değişimi bileşenlerde CSS flash yaratabilir; `data-theme` ilk render'da `<head>`-e yazılır.
- **Mobil table aşırı kaydırma:** 14K kayıtta sütun sayısı artarsa; performans için sanal kaydırma (IntersectionObserver) eklenebilir.
- **Modal z-index çakışması:** Tasks overlay `z-index:9998`, modal `10000`; yeni overlay'ler artan sayaçla yönetilmeli.

---

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

**Brief tamamlandı. Öneriler güncel sistem analizi ve gelecek planı için hazırlanmıştır.**
