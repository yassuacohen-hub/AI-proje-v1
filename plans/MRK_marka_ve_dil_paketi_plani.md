# MRK — Marka Konumlandırma ve Dil Paketi Planı

> Durum: **Onaylandı (sahip)** · Tarih: 2026-09-14 · Sahip kararlarıyla kesinleşti.
> Bu dosya Code moduna geçişte bağlam taşıyıcısıdır. Uzun anlatım yok; karar + adım.
> **Marka kiti konumu (MARKA-REVIZE-01, D-44):** Kurumsal kimlik seti (marka metni, logo,
> web/pazarlama prompt'ları, tasarım token'ları) artık `docs/brand/` altındadır; bu plandaki
> eski "kök dizin" atıfları o klasörü kasteder. Teknik SSOT: `docs/AJAN_DETAY.md` §11.

---

## 1. Kesinleşen Marka Kararları (SSOT)

| Port | Teknoloji | Marka | Rol | Renk kimliği |
|---|---|---|---|---|
| 8000 | HTML/CSS/JS | **HUGINN** 🦅 | Süper Kullanıcı Paneli — canlı izleme, telemetri, analitik | siber yeşil / elektrik mavisi |
| 8501 | Streamlit | **MUNINN** 🛡️ | Süper Admin Paneli — denetim, log, kök ayar, güvenlik | mat siyah / koyu antrasit |
| — | `src/company_master/*` | **ODIN** ⚡ | Çekirdek — DB, middleware, ortak utils | gece mavisi + fırtına grisi + altın |

**Ek kararlar:**
- Huginn (8000) **görsel tasarımı ayrı bir tur** olarak ertelendi. Bu turda 8000'e dokunulmaz.
- Dil paketi dağıtımı: **build adımı** ile tek kaynaktan JS'e üretim (ayrı JSON tutmak yasak).
- İsim göçü **kademeli**; toplu rename/refactor bu turda yapılmaz.

---

## 2. Dil Paketi Mimarisi

### 2.1 Neden iki katman?

Eldeki 107 anahtar bir i18n kataloğu değil, **marka sesi** koleksiyonu ("Sistemin nabzı tutuluyor, her diyar sakin."). Gerçek arayüzde gereken buton/kolon/hata metinleri yok. Tek dosyada birleştirilirse kodda hardcoded Türkçe kalmaya devam eder ve "hardcoded metin yasak" kuralı ilk gün çiğnenir.

```
src/company_master/i18n/
├── ses.json          # MARKA SESİ — atmosfer, karşılama, uyarı tonu (107 + yeni 6 kategori)
├── ui.json           # İŞLEVSEL — buton, kolon, form hatası, kuru etiketler (zamanla dolar)
├── __init__.py       # t() / ses() / sayi() / tarih() genel API
├── ton.py            # ton→renk/ikon eşlemesi (marka disiplini motoru)
└── disa_aktar.py     # messages.js üretici (Huginn/8000 için, ileride)
```

### 2.2 Anahtar şeması (ton + katman + seviye) — ✅ SAHİP ONAYLI

İki eksen vardır ve bunlar karıştırılmaz:

**Eksen 1 — `katman`: oyun neyin üstünde oynanır?**

| Katman | İçerik | Ton |
|---|---|---|
| `veri` | Sayı, durum, hata kodu, tablo başlığı, para, tarih, yasal uyarı | ❄️ Kuru, kesin, **mitolojisiz** |
| `cerceve` | Sayfa başlığı, boş durum, ipucu, yükleme, başarı, onboarding | 🦅 Mitolojik, anlatısal |

> **Demir kural:** Müşterinin karar verdiği hiçbir rakam veya hata mitolojik dile bürünmez.
> Oyunlaştırma asla verinin üstüne çıkmaz → "oyun müşteriyi yanıltır" riski sıfırlanır.

**Eksen 2 — `seviye`: kullanıcı olgunluğu (yalnız `cerceve` katmanında)**

`cirak` = uzun, açıklayıcı, öğretici → yeni müşteri paneli **öğrenir**
`usta` = kısa, kuru → deneyimli kullanıcı **yavaşlamaz**

`veri` katmanı — tek varyant:

```json
"odin_baglanti_koptu": {
  "tr": "Bağlantı kesildi (503). Yeniden deneniyor.",
  "en": "Connection lost (503). Retrying.",
  "katman": "veri",
  "ton": "danger",
  "ikon": "cloud_off"
}
```

`cerceve` katmanı — çırak/usta varyantlı:

```json
"huginn_akis_bos": {
  "tr": {
    "cirak": "Huginn ufku tarıyor, henüz bir haber yok. Canlı akış sistemdeki olayları anında buraya düşürür.",
    "usta": "Akışta kayıt yok."
  },
  "en": "No records in the stream.",
  "katman": "cerceve",
  "ton": "info",
  "ikon": "radar"
}
```

**Kurallar:**
- `usta` yoksa `cirak`'a düşülür → her anahtara iki metin yazma zorunluluğu **yok**
- `en` dili **tek varyant** (usta karşılığı) → anahtar başına 4 metin bakım kâbusu önlenir
- `veri` katmanında `tr` değeri **daima düz string**; obje verilirse test kırar
- Seviye kaynağı: ayarlardan "Kuzgun Rehberi" aç/kapa; varsayılan ilk girişlerde `cirak`

`t()` metin + **ton + ikon + katman** döndürür → geliştirici renk seçmez, **marka seçer**.
Geçerli tonlar: `info` · `success` · `warning` · `danger` · `neutral`
Geçerli katmanlar: `veri` · `cerceve`

### 2.3 Adlandırma sözleşmesi

```
{marka}_{alan}_{durum}
huginn_akis_basladi · muninn_denetim_bos · odin_baglanti_koptu
```

### 2.4 Parametreli mesaj

```json
"muninn_kayit_arsivlendi": "Muninn hatırlayacak: {sayi} kayıt {kullanici} tarafından arşivlendi."
```
`t("muninn_kayit_arsivlendi", sayi=12, kullanici="yasin")`

### 2.5 Fallback zinciri

Dil: `istenen dil → tr → anahtarın kendisi` — **asla KeyError fırlatmaz**, UI çökmez.
Seviye: `istenen seviye → cirak → düz string`
Dil kaynağı: `st.session_state["dil"]` → `user_settings` → `tr`.
JSON `@lru_cache` ile tek kez okunur.

---

## 3. Eklenecek 6 Eksik Kategori (yaratıcı katkı)

| Kategori | Örnek anahtar | Taslak metin |
|---|---|---|
| Boş durum | `huginn_liste_bos` | "Huginn ufku taradı, henüz bir şey yok." |
| Hata / kurtarma | `odin_baglanti_koptu` | "Bifröst kesildi. Bağlantı yeniden kuruluyor…" |
| Onay | `muninn_geri_alinamaz` | "Bu iz kalıcıdır. Muninn unutmaz. Devam edilsin mi?" |
| Yükleme | `huginn_tarama_suruyor` | "Huginn dokuz diyarı tarıyor…" |
| Yetki | `muninn_taht_yetkisiz` | "Bu tahta oturma yetkiniz yok." |
| Başarı | `odin_muhurlendi` | "Mühürlendi. Sistem kararlı." |

---

## 4. Bekçi Testleri (`tests/test_i18n.py`)

1. `tr` ve `en` anahtar kümeleri **birebir eşit** (eksik çeviri yakalanır)
2. Hiçbir değer boş değil
3. Bilinmeyen anahtar çökmez, anahtarın kendisini döner
4. Her anahtar `huginn_|muninn_|odin_` prefix'lerinden biriyle başlar
5. Her anahtar en az **3 parçalı** (`marka_alan_durum`)
6. `ton` alanı yalnızca geçerli 5 değerden biri
7. `{param}` içeren mesajda eksik parametre → açık hata (sessiz bozulma yok)
8. **`katman` alanı zorunlu** ve yalnız `veri|cerceve`
9. **`veri` katmanında `tr` düz string** olmalı (seviye çatallanması yasak)
10. **`veri` katmanında mitolojik sözcük yasağı** — yasak listesi: `Huginn, Muninn, Odin, Bifröst, diyar, kuzgun, taht, mühür` (marka adı geçse bile `veri` metni anlatısallaşmaz)
11. `cerceve` + obje değerinde **`cirak` anahtarı zorunlu** (usta opsiyonel)
12. `en` değeri **asla obje değil** (tek varyant kuralı)
13. Marka yazımı: `Huggin\b|Hugginn|Hugin\b|Munin\b|Muginn|Munnin|Odinn|Odın` gibi hatalı yazımlar hiçbir metinde geçmez; tarama kapsamı `docs/brand/**/*.md` dahil tüm marka dokümanlarıdır (test ile zorlanır: `tests/test_i18n.py`)

---

## 5. Pilot Kullanım Noktaları (düşük risk, 4 nokta)

| Anahtar | Dosya |
|---|---|
| `odin_command_center` | `app.py` → `render_sidebar` marka başlığı |
| `odin_ai_co_pilot` | `src/company_master/ui/components/topbar.py` → `ChatBubble._not_html` |
| `huginn_dashboard_welcome` | `web_dashboard/tabs/ana_kontrol.py` giriş paragrafı |
| `muninn_audit_trail_ready` | `web_dashboard/tabs/admin_audit.py` giriş |

> Not: `huginn_*` anahtarının Muninn panelinde kullanılması geçici bir tutarsızlıktır; Ana Kontrol ekranı canlı izleme yüzeyi olduğu için marka açısından Huginn ailesindedir. Sitemap sonrası netleşecek.

---

## 6. Doküman ve Obsidian Göçü

| Kaynak | Hedef |
|---|---|
| `../proje_kapsam_ve_konumlandirma.md` | `AI proje v1/V10/00_ana_belgeler/03_marka_konumlandirma_ve_kapsam.md` |
| ⟶ ayna | `docs/MARKA_KONUMLANDIRMA.md` (kısa stub + V10 linki) |
| `../projemdeki dil klasörüne...json` | `src/company_master/i18n/ses.json` (şemaya dönüştürülerek) |

- Yeni dosyaya YAML frontmatter: `tags: [marka, konumlandirma, huginn, muninn, odin]`
- `AI proje v1/V10/00-Home.md` → `[[03_marka_konumlandirma_ve_kapsam]]` bağı
- Çapraz bağ: Muninn PRD ↔ marka dokümanı ↔ `06_muninn_prd_vs_huginn_analiz`
- **Düzeltme:** `02_hugins_master_kaynak_dokumani.md` → `02_huginn_master_kaynak_dokumani.md` (yazım hatası, bağlar da güncellenir)
- "Kesip yapıştır" = kaynak dosyalar üst dizinden **silinir** (sahip onayladı)

---

## 7. Kural Dosyalarına İşlenecek Blok

Hedef: `ANA_KURALLAR.md`, `AGENTS.md`, `.roorules`, `.clinerules`

```
## Marka Terminolojisi (Odin / Huginn / Muninn)
- HUGINN = Düşünce → 8000 / HTML — canlı izleme, telemetri, analitik
- MUNINN = Hafıza  → 8501 / Streamlit — denetim, log, kök ayar, güvenlik
- ODIN   = Çekirdek → src/company_master — DB, middleware, ortak utils
- Kullanıcıya görünen metinler i18n anahtarından gelir; hardcoded Türkçe metin yasaktır.
- Doküman camelCase örnekler verir; Python tarafında SNAKE_CASE zorunludur:
  fetchActiveUsers() → aktif_kullanicilari_getir()
  writeToMemory()    → hafizaya_yaz()
```

### Marka Sözlüğü (ajanlar için)

| Kaçın ❌ | Kullan ✅ |
|---|---|
| "Log" | "Muninn Hafızası" |
| "Real-time" | "Huginn Akışı" |
| "Sistem" (genel) | "Odin Çekirdeği" |
| "Silindi" | "Arşivlendi / hafızaya işlendi" |

---

## 8. Paket → Kuzgun Mantıksal Haritası

> **Fiziksel taşıma YAPILMAZ.** Kaynak doküman `src/modules/{huginn,muninn,odin}/` önerir; mevcut proje `src/company_master/` altında 25 paket kullanır. Birebir taşıma yüzlerce import kırar ve 1426 testi yakar. Yalnızca mantıksal aidiyet tanımlanır.

| Kuzgun | Mevcut paket / ekran |
|---|---|
| **ODIN** | `db`, `schema`, `cache`, `utils`, `gateway`, `auth`, `logging`, `settings` |
| **HUGINN** | `admin_realtime`, `ana_kontrol`, `admin_api_analytics`, `admin_kpi`, `webhook_monitor` |
| **MUNINN** | `admin_audit`, `admin_panel` (karar defteri), `admin_dlq`, `admin_sistem`, `orchestrator` |

---

## 9. Açık Riskler ve Çelişkiler

1. **"Muninn silmez" vs gerçek DELETE** — ✅ **KARAR (S7):** Metinde "arşivlendi" denir. Şema, soft-delete, DB **değişmez**. Yalnız sözlük maddesi.
2. **Palet çatallanması test kırar** — `tests/test_ui_kontrast.py`, `test_theme_system.py`, `test_ui_components.py::_ZORUNLU_RENKLER` sabit renk sözleşmeleri içerir. Muninn paleti uygulanırsa bu testler marka paletine göre güncellenmelidir. *Bu tur kapsam dışı (Huginn tasarımı ayrı tur).*
3. **Altyapı adları** — ✅ **KARAR (S1): "Tarihsel Çatı Adı" kuralı.** `huginn` DB adı, repo adı, `HuginnMCPServer`, `admin@huginn.local` **hiç değişmez**. Hiçbir rename/migration yapılmaz. Yalnızca kural dosyasına ayrım cümlesi yazılır: *"`huginn` altyapıda görülürse tarihsel çatı adıdır, panel markası değildir; panel için daima `huginn_panel` / `muninn_panel` açık eki kullanılır."* Sıfır migration riski.
4. **`en` dili** — ✅ **KARAR (S3/S9):** Altyapıda hazır bekler, arayüzde dil seçici yok. `en` **tek varyant** (çırak/usta çatallanması yok).
5. **Şema derinliği geri dönüşü pahalı** — `katman` + `seviye` alanları başta kurulmazsa sonradan tüm anahtarlar yeniden yazılır. ✅ Sahip onayıyla **şimdi** kuruluyor.

---

## 10. Onaylanan Kararlar Özeti (S1–S12)

| # | Konu | Karar |
|---|---|---|
| S1 | Altyapı isim göçü | **Tarihsel Çatı Adı** — hiçbir rename yok, yalnız doküman ayrımı |
| S2 | Süper Kullanıcı / AI | Ödeme yapan müşteri; AI = Huginn (canlı) + Muninn (log) beslemeli RAG asistanı |
| S3 | Dil seçici UI | Yok; `en` altyapıda bekler |
| S4 | TXT kaynakları | İçeri **alınmaz**; sahip taslak olarak yeniden hazırlayacak |
| S5 | Ton | **Katman ayrımı + Yolculuk** — `veri` kuru / `cerceve` mitolojik; `cirak`/`usta` seviyeleri |
| S6 | Multi-tenant | Tek kiracılı demo; `tenant_id` gelecekte (iş modeline bağlı) — **TEN-01** |
| S7 | Muninn silmez | Metinde "arşivlendi"; şema değişmez |
| S8 | Rozet ilerlemesi | Ayrı görev **GAM-01**; bu turda kurulmaz |
| S9 | `en` çatallanması | Hayır — tek varyant |
| S10 | Marka yazımı | `Huginn/Muninn/Odin` çevrilmez; `Huggin/Hugginn/Hugin/Munin/Muginn/Munnin/Odinn/Odın` yazımları **yasak** (test ile zorlanır) |
| S11 | AI görünen adı | **AÇIK** — "Abrakadabra" (mevcut) vs **MIMIR** 🗿 önerisi; teknik ad `odin_ai` |
| S12 | Oyunlaştırma ölçümü | Şimdilik ölçüm kurulmaz; rozet olayları ileride audit log'a düşer |

---

## 11. Ertelenen Ayrı Görevler

- **GAM-01 — Rozet / Keşif Sistemi:** 👁️ Huginn'in Gözü (canlı akışı ilk izleme), 🧠 Muninn'in Hafızası (ilk denetim kaydı), ⚡ Odin'in Tahtı (ilk kök ayar). Kilitli rozet = **henüz keşfedilmemiş özellik** → puan değil, özellik haritası. İlerleme saklama: `data/kullanici_ilerleme.json`, DB gelince taşınır.
- **TEN-01 — Multi-tenant:** `tenant_id`, KVKK ayrımı, faturalama. İş modeli netleşince. *Bu turda multi-tenant'ı imkânsız kılan varsayım (global singleton ayar vb.) üretilmeyecek.*
- **AI-CHAT-01 — Odin AI / RAG motoru:** Huginn canlı veri + Muninn audit log → asistan. Görünen ad S11 kararına bağlı.

---

## 12. Uygulama Sırası

1. `i18n/` paket iskeleti + `ses.json` şema dönüşümü (katman/seviye/ton/ikon)
2. 6 eksik kategori eklenmesi
3. `t()` / `ton.py` / `sayi()` / `tarih()` motoru
4. `tests/test_i18n.py` bekçileri (**13 madde**)
5. 4 pilot kullanım noktası
6. `disa_aktar.py` → `messages.js` üretici
7. Doküman göçü + Obsidian bağlamı
8. Kural dosyaları + marka sözlüğü + güvenlik supabı + Tarihsel Çatı Adı
9. Tam regresyon + teslim
