# Admin Panel UX Audit ve Premium Arayuz Plani

Tarih: 2026-09-14
Kapsam: Streamlit admin paneli, `app.py`, `web_dashboard/tabs/`, `web_dashboard/css/style.css`

## Kisa karar

Mevcut panelin bilgi mimarisi onceki haline gore belirgin bicimde iyilesti: sidebar navigasyonu, grup basliklari, breadcrumb, aktif bolum vurgusu, cache yenileme ve bos-veri metinleri dogru yonde. Ancak istenen Linear/Stripe/Vercel seviyesindeki enterprise admin urunu henuz degil. Su anki urun iyi bir operasyon prototipi; premium SaaS kabugu, veri sozlesmeleri ve erisim/aksiyon akislari tamamlanmamis.

## Iyi yapilanlar

- `app.py` tek kaynakli bolum kayit defteri ve gruplu sidebar kullaniyor.
- Hazir olmayan bolumler sessizce kirilmak yerine acik placeholder gosteriyor.
- Ana Kontrol'de musteri metrikleri ile sistem metrikleri ayriliyor.
- Sistem, yonetim, KPI, kalite, maliyet ve analitik modulleri ayrik tutulmus.
- Empty-state ve cache yenileme davranislari bircok sekmede ele alinmis.
- Testler loader, render-contract ve bozuk veri senaryolarini kapsiyor.

## Kritik UX eksikleri ve hatalar

### P0: Urun modeli ile istenen panel modeli uyusmuyor

Revenue, transaction, conversion, retention, moderation queue, appeal ve ban/suspension akislari icin mevcut backend veri sozlesmesi yok. Bu kartlari sahte veriyle eklemek guveni bozar. Once endpoint/schema ve veri sahipligi tanimlanmali; yoksa bu bolumler acikca "planlandi" durumunda kalmali.

### P0: Musteriler ekrani henuz gercek enterprise workflow degil

Liste ve filtre var, ancak satir secimiyle acilan profile drawer, activity history, role/permission, suspend/ban ve audit action akisi yok. Kullanici listesi ile firma listesi kavramsal olarak da ayrilmali: musteri tenant/kullanici, firma ise veri varligi.

### P0: Sidebar mevcut ama collapsible degil

Sidebar tum alanı kapliyor; dar ekran, klavye ile gecis ve responsive collapse davranisi eksik. `st.sidebar` ile CSS/JS web panelinin iki farkli navigasyon modeli yan yana yasiyor. Tek bir bilgi mimarisi ve tek aktif durum kaynagi gerekli.

### P1: Topbar ve global komut yuzeyi eksik

Arama, bildirim merkezi, kullanici profili, son yenileme, ortam/tenant bilgisi ve klavye kisayollari tek bir ust barda birlesmemis. Footer'daki cache butonu operasyonel birincil aksiyon gibi gorunuyor.

### P1: Veri yogunlugu ve hiyerarsi

17+ modulu tek uygulamada tutmak buyuk; kartlar ve alt basliklar artinca tarama maliyeti yukseliyor. Her sekmede ayni baslik/caption/yenile/info kalibi tam standart degil. Metrik aciklamalari bazen soru formatinda ama aksiyon ve drill-down baglantisi yok.

### P1: Renk ve tasarim sistemi talebiyle mevcut tema farkli

Mevcut CSS koyu, mavi/purple agirlikli ve radius degerleri 8-12px. Istenen 20px radius, light/dark mode, Indigo `#6366F1`, success/warning/danger tokenlari uygulanmamis. Ancak tum komponentleri 20px yuvarlamak enterprise scan ergonomisini bozabilir; panel/kart icin 12-16px, kontrol icin 8-10px daha uygun bir denge.

### P1: Responsive ve erisilebilirlik kaniti yok

Kucuk ekran, focus order, keyboard navigation, focus-visible, contrast, table overflow ve screen-reader label testleri eksik. Streamlit widget'lari icin en azindan Playwright Faz 2 planlanmali; bu sprintte render-contract + manuel acceptance checklist tutulmali.

### P1: Loading/error/empty state dili parcalı

Bazi moduller spinner, bazilari info, bazilari warning kullaniyor. Hata mesajlari teknik ayrinti ile kullanici eylemini ayni yerde vermiyor. Ortak state kontrati olmadan premium gorunum tutarsiz kalir.

### P2: Islevsel kapsam eksikleri

Moderation, spam, appeal, audit action history, notification preferences, user profile menu, transaction detail ve export permission akislari yok. Bunlar UI karti olarak degil, rol ve audit kurallariyla birlikte planlanmali.

## Onerilen bilgi mimarisi

1. **Ana Kontrol**: musteri/sistem KPI, uyarilar, son aktiviteler.
2. **Musteriler**: tenant/kullanici listesi, filtreler, profile drawer, aktivite ve aksiyonlar.
3. **Gelir ve Paketler**: plan, kredi, fatura ve transaction; veri yoksa planli durum.
4. **Pazarlama**: kampanya, segment, conversion funnel.
5. **Sistem**: performans, webhook, DLQ, maliyet, API analitigi.
6. **Yonetim**: roller, API anahtarlari, audit, export, ayarlar.
7. **Abrakadabra**: AI operasyon asistani; provider/fallback ve maliyet bilgisiyle.

Sidebar iki kategoriye ayrilmali: Is ve Sistem. Collapsed durumda ikon + tooltip; acik durumda etiket + kisa aciklama. Aktif bolum URL/session state ile tek kaynaktan yonetilmeli.

## Tasarim sistemi

- Tokenlar: `--color-bg`, `--color-surface`, `--color-border`, `--color-text`, `--color-accent: #6366F1`, `--color-success: #22C55E`, `--color-warning: #F59E0B`, `--color-danger: #EF4444`.
- Light/dark tema tokenlari ayni semantik adlari kullanmali.
- 12 kolon grid mantigi; ana icerik `minmax(0, 1fr)`, yan drawer sabit ve responsive.
- Kart radius: 12-16px; modal/drawer 16-20px; buton 8-10px.
- Skeleton, empty, warning, error ve success state'leri ortak komponent/yardimci ile standardize edilmeli.
- Motion: sayfa acilis stagger ve drawer transition ile sinirli; tablo ve KPI'da dekoratif animasyon yok.

## Tasarim kararları ve taşınabilir mimarı

### Faz 1 temel kabuk gereksinimler

1. **Token sistemi:** `web_dashboard/css/admin_tokens.css` oluşturuldu.
   - Semantik `--color-*` adlandırması (bg/surface/border/text/accent/success/warning/danger).
   - Light (`:root`, açık tema) ve dark (`[data-theme="dark"]`, koyu tema) override'ları.
   - Indigo accent `#6366F1`, success `#22C55E`, warning `#F59E0B`, danger `#EF4444`.
   - Radius bands: `--radius-button: 8px`, `--radius-card: 12px`, `--radius-modal: 16px`.
   - Admin-specific surfaces: topbar, sidebar, drawer, shadow (light/dark fark).
   - Responsive grid breakpoints: 1440px (12-col) / 1024px (8-col) / 640px (4-col).
   - Erişilebilirlik: `@media (prefers-reduced-motion: reduce)` ile geçiş devre dışı.

2. **UI bileşen kütüphanesi:** `src/company_master/ui/` (UX-01) tamamlandı.
   - 9 bileşen (Button/Input/Dropdown/Badge/Card/MetricCard/Table/Modal/Tooltip).
   - 82 test: CSS/XSS/a11y coverage + Copilot design contract (token sözleşmesi).
   - Bileşen CSS'i (`styles.py`) token'lara bağlı; ham renk yok.
   - Sonraki aşama: admin shell bileşenleri (Topbar, Sidebar, Drawer, ProfileMenu).

3. **Shell mimarisi (Faz 1):**
   - **Topbar:** Logo, global search, notification bell (placeholder), profile menu, tema toggle.
     - Responsive: mobile'da collapsed search + hamburger menu.
   - **Sidebar:** Collapsible (icon + tooltip / label + description).
     - Kategori: "İş" (Ana Kontrol, Müşteriler, Gelir/Paketler, Pazarlama) ve "Sistem" (Sistem, Yönetim, Abrakadabra).
     - Aktif durum: URL seşme (query param `?bolum=...`) + session state.
     - Responsive: 1024px altında overlay veya drawer.
   - **Main grid:** 12-column; sidebar fixed/collapsible, ana içerik `minmax(0, 1fr)`.
   - **Drawer:** Profile, filter, admin action UI (profile drawer, audit drawer vs).
   - **Notification + Loading/Error/Empty state:** Ortak dil ve kontrat.

### Faz 1: Kanit ve kabuk

- Dashboard shell: topbar, collapsible sidebar, command/search, notification placeholder, profile menu.
- Design token dosyasi ve light/dark toggle.
- Her sekme icin render contract: data source, empty, loading, error, refresh, permission.
- P0 veri olmayan moduller icin "planli" state; sahte revenue/transaction yok.
- Admin bileşenleri (Topbar, Sidebar, Drawer) Faz 1b'ye taşınıyor; Faz 1a kabuk öncelikli.

### Faz 2: Musteri operasyonu

- User/tenant ayrimi, advanced filters, profile drawer, activity history.
- Role/permission ve ban/suspension aksiyonlari.
- Her aksiyon JSONL audit kaydi ve confirmation/error state.

### Faz 3: Olcum ve gelir

- Revenue/transaction/conversion/retention endpointleri ve veri freshness metadata.
- Funnel/heatmap/retention charts; export ve timezone tanimi.

### Faz 4: Moderation ve guvenlik

- Reports queue, spam scoring, appeal workflow, RBAC, audit search.
- Kritik aksiyonlarda idempotency, confirmation ve reversible operation.

## Kabul kriterleri

### Faz 1a Responsive + Accessibility Checklist (Desktop / Tablet / Mobile)

| Kontrol | Desktop 1440px | Tablet 1024px | Mobile 390px | Durum |
|---|:---:|:---:|:---:|---|
| **Layout** | | | | |
| Sidebar/main grid layout doğru oran | ✓ | ✓ (sidebar collapse) | ✓ (drawer overlay) | TODO |
| Topbar tüm kontrolleri görünür | ✓ | ✓ (search collapsed) | ✓ (menu collapsed) | TODO |
| Main content `minmax(0, 1fr)` responsive | ✓ | ✓ | ✓ (single column) | TODO |
| Drawer/modal overflow + scrolling | ✓ | ✓ | ✓ (viewport-high) | TODO |
| **Keyboard Navigation** | | | | |
| Tab order: topbar → sidebar → content → drawer | ✓ | ✓ | ✓ | TODO |
| Sidebar collapsible enter/esc ile toggle | ✓ | ✓ | N/A (hammer menu) | TODO |
| Search + filter form aria-label + submit | ✓ | ✓ | ✓ | TODO |
| Modal/drawer: focus trap + close button/esc | ✓ | ✓ | ✓ | TODO |
| **Accessibility** | | | | |
| Focus visible (outline/ring) tüm kontrollerde | ✓ | ✓ | ✓ | TODO |
| Landmark roles: banner (topbar), navigation (sidebar), main, complementary (drawer) | ✓ | ✓ | ✓ | TODO |
| Metrik kartları data table / data list semantiği | ✓ | ✓ | ✓ | TODO |
| Table header `scope="col"` + th | ✓ | ✓ | ✓ | TODO |
| Form kontrolleri label + aria-describedby (hata/yardım) | ✓ | ✓ | ✓ | TODO |
| Icon buttons aria-label (no text) | ✓ | ✓ | ✓ | TODO |
| Color contrast WCAG AA (4.5:1 metin, 3:1 UI) | ✓ | ✓ | ✓ | TODO |
| Tooltip, popover aria-describedby + role | ✓ | ✓ | ✓ | TODO |
| Screen reader: empty state, loading, error mesajları | ✓ | ✓ | ✓ | TODO |
| **UX** | | | | |
| Tek birincil aksiyon (sekmede vurgulanmış buton) | ✓ | ✓ | ✓ | TODO |
| Empty state: ikon + açıklama + aksiyon | ✓ | ✓ | ✓ | TODO |
| Loading: spinner + "Yükleniyor..." | ✓ | ✓ | ✓ | TODO |
| Error: ikon + mesaj + retry buton | ✓ | ✓ | ✓ | TODO |
| Son güncelleme timestamp + manual refresh | ✓ | ✓ | ✓ | TODO |
| Dark mode toggle (topbar) + `[data-theme="dark"]` persist | ✓ | ✓ | ✓ | TODO |

### Veri sözleşmesi garantisi

- Revenue, transaction, conversion, retention, moderation endpointleri **tanımlanana kadar**
  bu sekmeler "Planlanan" durumunda kalır (sahte veri / skeleton no).
- Her sekme: `render_contract` test (data source, empty, loading, error, field schema).
- Audit log + permission kontrolü sadece backend schema tamamlandığında uygulanır.

### Test kapsamı (Faz 1a)

- En az render-contract testleri (load / empty / error / permission scenarioları).
- CSS syntax kontrolü + light/dark theme token coverage.
- Responsive (Playwright smoke, Faz 2'de tam).
- Kritik aksiyonlar (admin approvals vb.) Faz 2'de audit trail ile.
