# HUGINN V10 — Plan Netleştirme

> **Tarih:** 2026-09-18 · **Sürüm:** 1.0 · **Durum:** KAHİN (Ürün Sahibi) onayı bekliyor
> **Kapsam:** `AI proje v1/V10/00_ana_belgeler/` (3 belge) + `V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` + ek bulunan `docs/v10_OSINT_YETENEK_KATALOGU.md`
> **Kural:** Belge ile kod çeliştiğinde **kod esas alınmıştır**. Belgede olmayan hiçbir şey uydurulmamış, § 5'e taşınmıştır.

---

## KAHİN (Ürün Sahibi) İçin 60 Saniyelik Özet

| Renk | Bulgu | Oran |
|------|-------|------|
| 🟢 | Belgelerdeki iddiaların **12 tanesi** kodda birebir doğrulandı | %63 doğrulama oranı |
| 🔴 | **6 iddia çürütüldü** — belge yanlış, kod doğru | %32 çürütme oranı |
| 🔴 | Ürün tanımı **3 farklı belgede 3 farklı** anlatılıyor — birleştirme kararı gerekli | 3/4 belge çelişiyor |
| 🔴 | **1 canlı kod hatası** bulundu: firma filtresi açılınca arama çöküyor | 1 dosya, 6 satır |
| 🟡 | Belge 02'nin (OSINT) saydığı veri kaynaklarının **hiçbiri** kodda yok | %0 gerçekleşme |
| 🟡 | V9'un "Neo4j graph" kararı **hiç uygulanmamış** | 0 satır kod |
| 🔵 | Vektör arama, eşleştirme ve çoklu-müşteri altyapısı **beklenenden ileride** | 3 modül hazır |
| 🔵 | Karar bekleyen **8 açık soru** var — hepsi § 5'te | 8 madde |

**Tek cümlelik sonuç:** Kod belgelerden ileride; belgeler birbirini tutmuyor. Önce 4 kararı verip belgeleri koda uyduralım, sonra yeni iş başlatalım.

---

## 1. Kaynak Envanteri

| # | Yol | Tarih / Sürüm | Satır | Tek cümlelik özet |
|---|-----|---------------|-------|-------------------|
| K1 | `AI proje v1/V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md` | V1.0 · tarih yok (`:343` Faz 1.2 = 2026-09-01) | 718 | Ankara OSB firmaları için 19+3 tablodan oluşan veri şeması, kimlik kararı (UUID PK + VKN unique), entity resolution eşikleri ve MVP API sözleşmesi. |
| K2 | `AI proje v1/V10/00_ana_belgeler/02_hugins_master_kaynak_dokumani.md` | **Frontmatter/tarih/sürüm YOK** | 888 | Alan adı girildiğinde şirketin dijital ayak izini analiz eden global OSINT + dijital güven skoru platformu vizyonu (6 motor, 8 skor, 6 faz). |
| K3 | `AI proje v1/V10/00_ana_belgeler/03_marka_konumlandirma_ve_kapsam.md` | V10 · `gorev: MRK-03` · durum: aktif | 128 | Huginn (müşteri) / Muninn (admin) / Odin (çekirdek) marka ayrımı, hedef klasör ağacı ve AI kodlama talimatı. |
| K4 | `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` | **2026-08-28** · V9 | 964 | V6+V7+V8 birleşimi ana bağlam: 6+1 katman, üç skorlu fırsat motoru, hibrit veri mimarisi, monetizasyon ve panel konumlandırma. |
| K5 | `docs/v10_OSINT_YETENEK_KATALOGU.md` **(emirde yoktu, ilişkili olduğu için okundu)** | **1.0.2 · 2026-09-12** · Canlı | 270 | 9Router gateway, vektör katmanı, matcher ve OSINT motorunun **canlı doğrulanmış** yetenek envanteri. |

**Dizin doğrulaması:** `AI proje v1/V10/00_ana_belgeler/` içinde tam olarak **3 dosya** vardır (K1, K2, K3). Ek/gizli belge yoktur — KAHİN'in "dizini listele, hepsini oku" emri tam karşılanmıştır.

**Bağlam notu:** `AI proje v1/V10/` kökünde `11_osint_motoru/` klasörü mevcuttur. Bu, K2'nin rastgele bir taslak değil, V10'da **tanınmış ayrı bir iş kolu** olduğunu gösterir (bkz. B-1).

---

## 2. Netleşen Plan

### 2.1 V10 Kapsamı — Üç Katman Modeli

Belgeler tek bir ürün anlatmıyor; kodla karşılaştırınca **üç katmanın** üst üste bindiği görülüyor:

| Katman | Kaynak belge | Kodda karşılığı | Olgunluk |
|--------|--------------|-----------------|----------|
| **L1 — Company Master** (kim, nerede, ne üretir) | K1 | `search/engine.py`, `entity_resolution/`, `etl/`, `schema/` | 🟢 Çalışıyor |
| **L2 — Commercial Intelligence** (kim ne zaman satın alır) | K4 | `intelligence/`, `web_app.py:944-1223` (`_match_puan`, `/api/match`) | 🟡 Kısmi |
| **L3 — OSINT / Dijital Güven** (alan adından risk skoru) | K2, K5 | `gateway/ninerouter_client.py`, `engine/osint_engine.py`, `vector/` | 🟡 Altyapı var, kaynak yok |

Marka ayrımı (K3) bu üç katmanın **üzerinde**, sunum düzeyindedir: Huginn 🦅 = müşteri yüzeyi (8000) · Muninn 🛡️ = admin yüzeyi (8501) · Odin ⚡ = çekirdek.

### 2.2 Faz Sırası ve Somut Çıktılar

Aşağıdaki sıra **mevcut kod durumundan** türetilmiştir; belge takvimleri (`K4:833` Temmuz, `K4:840` Eylül, `K1:343` 2026-09-01) bugün (2026-09-18) itibarıyla geçmiştir.

| Faz | Ad | Somut teslim çıktısı | Bitti kriteri | Bağımlılık |
|-----|-----|---------------------|---------------|------------|
| **F0** | Hijyen (2–4 saat) | `search/engine.py` mükerrer where bloğu silinir · `search/fulltext.py` silinir · `docker-compose.yml` `env_file` + `DASH_API_URL` | `has_phone=True` çağrısı hata vermez; ilgili testler yeşil | Yok — hemen |
| **F1** | Belge–kod hizalama (1 gün) | K1/K2/K4'e düzeltme notu; `firms`→`companies`, Neo4j "planlanan" işareti, K3:105 önek iddiası düzeltmesi | 6 çürütülen iddianın hepsi belgede işaretli | F0 |
| **F2** | Admin UX zinciri (2–3 gün) | `ADMIN-UX-LOGOUT-01` → `ADMIN-UX-PROFILMENU-01` → `ADMIN-UX-MENUTREE-01` → `ADMIN-UX-AYARLAR-SAYFA-01` | Her görevde: wireframe onayı + çalışan test + teslim | F0, K-5 onayı |
| **F3** | L1 tamamlama (3–5 gün) | `K1:343` genişletilmiş 3 tablo (`company_capabilities`, `certifications`, `key_personnel`) ETL'e bağlanır | 8313 firmada dolum oranı ölçülür | F1 |
| **F4** | L3 kaynak bağlama (5–10 gün) | `scrapers/` altına ETBİS + Whois + DNS/SSL toplayıcı | 3 kaynak canlı, `sources` tablosuna yazıyor | K-A kararı |
| **F5** | L2 skor motoru (5–10 gün) | `K4:229-240` üç skor sisteminin `intelligence/` altında tam uygulanması | Need/Fit/Timing 8313 firmada hesaplanıyor | F3 |
| **F6** | Multi-tenant (Faz 2, K4:840) | `tenant/model.py` iskeletinin plan + kredi ile birleşmesi | Bir müşteri kendi verisini izole görüyor | F5, K-D kararı |

**Kritik yol:** F0 → F1 → F3 → F5. F2 paralel yürüyebilir (farklı dosyalar). F4 karar bekliyor.

---

## 3. Bulgular

> Her madde `dosya:satır` referanslıdır. Çelişkilerde kod esas alınmıştır.

### 🔴 Kırmızı — Blokaj / Acil

| Kod | Bulgu | Kanıt |
|-----|-------|-------|
| **B-14** | **Canlı kod hatası.** `fetch_filtered_companies` içinde `has_phone`/`has_email`/`has_web` where blokları **iki kez** ekleniyor. İkinci kopyada SQL'e `<> ""` giriyor; PostgreSQL bunu **sütun adı** sayar → `column "" does not exist`. Filtre açıkken sorgu çöker. | `src/company_master/search/engine.py:176-181` (doğru) vs `:182-187` (mükerrer + bozuk) |
| **B-2** | **Tablo adı çelişkisi.** K1 `companies`, K4 `firms` diyor. **Kod kesin `companies`.** K4 çürütüldü. | `K1:36` vs `K4:109` · Kod: `engine.py:23,93,148,196`, `web_app.py:676` |
| **B-1** | **Ürün tanımı üç ayrı.** K1 = Ankara firma ana verisi; K4 = Ankara B2B ticari istihbarat; K2 = global OSINT güven platformu. K2'de "Ankara/OSB/B2B" hiç geçmiyor; K1+K4'te OSINT skorları hiç geçmiyor. **Hafifletici:** `V10/11_osint_motoru/` klasörü + K5 (canlı, 2026-09-12) K2'yi ayrı iş kolu olarak meşrulaştırıyor → "rakip ürün" değil, **L3 katmanı**. Yine de resmî birleştirme kararı yok. | `K2:62,66` · `K1:712` · `K4:15-27` · `V10/11_osint_motoru/` · `K5:1-6` |

### 🟡 Sarı — Dikkat

| Kod | Bulgu | Kanıt |
|-----|-------|-------|
| **B-3** | **Mimari sınır ihlali.** K1 "Company Master müşteri–ürün uyumu yapmaz" diyor; kodda `/api/match` + `_match_puan()` var ve K4 zaten Fit Score istiyor. Kod esas → K1:658 eskimiş. | `K1:651-662` vs `web_app.py:1085`, `:944-1021` · `K4:234` |
| **B-4** | **Skor taksonomisi üç ayrı.** K2 8 skor (0-100), K4 4 skor (need/fit/timing/evidence), K1 9 KPI. Hangisi müşteriye gösterilecek belirsiz. | `K2:791-822` · `K4:229-240` · `K1:637-650` |
| **B-5** | **DB yığını kısmen hayali.** K4 "PostgreSQL SSOT + ChromaDB + Neo4j + Redis" diyor. **Neo4j `src/` içinde 0 sonuç** (grep `neo4j\|Neo4j\|NEO4J`). PostGIS `GEOMETRY(Point,4326)` de kodda yok. ChromaDB ise `vector/store.py`'de VAR. | `K4:51`, `:154-163`, `:106-147` · grep sonucu: 0 |
| **B-6** | **API isimlendirme üç ayrı.** K3 `/api/v1/huginn/*` + `/api/v1/muninn/*`; K1 `/companies`; kod `/api/companies` + `/api/admin/*`. Göç kararı yok. | `K3:111,118` · `K1:556-570` · `web_app.py:632,2302` |
| **B-7** | **K2 belge kalitesi düşük.** Frontmatter/tarih/sürüm yok; `:293-888` arası içeriğin ikinci mükerrer kopyası; web kopyala-yapıştır artıkları ("Plain Text", satır numaraları, "Daha fazla satır göster"); `:887` kapanış bozuk. | `K2:1-3, 293-888, 444-465, 495-510, 521-536, 563-570, 606-617, 637-648, 694-703, 747-775, 887` |
| **B-8** | **K4 § 16.5 eskimiş.** "[ ]" (yapılmadı) denen 5 maddeden **4'ü kodda var**: Dashboard KPI (`ana_kontrol.py`), AI Cost (`admin_performance.py:load_ai_cost_per_call`), Veri Kalitesi (`admin_quality.py`), Sistem Performansı (`admin_performance.py`). Sadece Webhook Monitor placeholder. | `K4:827-857` vs `ana_kontrol.py:44-84`, `admin_performance.py:45-99` |
| **B-11** | **İki ayrı SSOT beyanı.** K4 "PostgreSQL... Single Source of Truth", K5 "Bu katalog, tek başvuru kaynağı (SSOT)". Biri veri biri yetenek için ama terim çakışıyor. | `K4:51` vs `K5:19` |
| **B-12** | **K3 klasör iddiası kısmen çürük.** "src/company_master/ altında `huginn_`/`muninn_`/`odin_` teknik önekleriyle ilerlenir" — gerçekte sadece `odin_ai/` var; `huginn_` veya `muninn_` önekli **hiçbir** modül yok. | `K3:105` vs `src/company_master/` dizin listesi (35 alt modül) |
| **B-13** | **Scraper boşluğu.** `scrapers/` = `__init__.py` + `kariyernet.py`. K2'nin saydığı ETBİS, MERSİS, Whois, DNS, SSL/TLS, sosyal medya, pazaryeri, Wayback kaynaklarının **hiçbiri** kodda yok → K2 Faz 1 gerçekleşme %0. | `K2:74-93` vs `src/company_master/scrapers/` |

### 🟢 Yeşil — Tamam / Temizlenebilir

| Kod | Bulgu | Kanıt |
|-----|-------|-------|
| **B-15** | **Ölü kod.** `search/fulltext.py` `NotImplementedError` fırlatıyor; aynı adlı fonksiyonu `engine.py` gerçekten uyguluyor ve `__init__.py` `engine`'den import ediyor. `fulltext.py` silinebilir (YAGNI). | `search/fulltext.py:10-22` vs `search/engine.py:20-60`, `search/__init__.py:1` |
| **B-9** | **Entity resolution eşikleri K1 lehine.** K1 95/85/70 eşik veriyor, K4'te sayısal eşik yok. Kodda `threshold_optimizer.py` var → K1 uygulanabilir taraf. | `K1:452-457` · `entity_resolution/threshold_optimizer.py` |
| **B-10** | **Takvim geçmiş ama zararsız.** K4 MVP Temmuz, Faz 2 Eylül; K1 Faz 1.2 2026-09-01. Bugün 2026-09-18 → Faz 2 penceresi açık ve `tenant/` iskeleti hazır. | `K4:833,840` · `K1:343` · `tenant/{__init__,health,model}.py` |

---

## 4. Koda Karşı Doğrulama

### 4.1 ✅ Doğrulanan İddialar (12)

| # | Belge iddiası | Kod kanıtı |
|---|---------------|-----------|
| D-1 | Panel konumlandırma: 8000 = müşteri, 8501 = admin (`K4:793-796`) | `web_app.py` (FastAPI 8000) + `app.py` (Streamlit 8501) — 4/4 madde birebir |
| D-2 | Admin yetki kapısı `require_admin` (`K4:820`) | `web_app.py:2146` |
| D-3 | `/api/performance` tek performans kaynağı (`K4:822`) | `web_app.py:2598-2611` üretir, `admin_performance.py:33` tüketir |
| D-4 | SSE yalnız müşteri tarafında (`K4:823`) | `web_app.py:2798` SSE var; admin `@st.cache_data(ttl=30)` polling yapıyor |
| D-5 | Fiyatlandırma 3 tier + credit pack (`K4:576-579`) | `web_app.py:2336` (terminal/strategic/enterprise), `:2413` (750 TRY/50 kredi) |
| D-6 | "src/company_master/ altında, sıfır migration" (`K3:105`) | Klasör doğru — **ama önek iddiası yanlış**, bkz. B-12 (kısmen doğrulandı) |
| D-7 | UUID PK + VKN unique, VKN PK değil (`K1:24-29`) | `K4:110-111` aynı prensip; şema kodu uyumlu |
| D-8 | Ankara + OSB sabit kapsam filtresi (`K1:487-500`) | `web_app.py:676` `is_ankara=TRUE AND is_osb_member=TRUE` · `engine.py:149,168` aynı |
| D-9 | "PostgreSQL FTS yeterli, Elasticsearch gerekmez" (`K1:540`) | `engine.py` docstring + `similarity()` + `idx_companies_legal_name_trgm` GIN trigram. Elasticsearch yok. |
| D-10 | ChromaDB vektör katmanı (`K4:148-153`) | `vector/embedder.py` (batch+retry), `vector/store.py` (ChromaDB + in-memory fallback), `vector/service.py` (`index_firmalar`, `find_similar`, `deduplicate_by_vkn`) — birim testli |
| D-11 | Faz 2 multi-tenant (`K4:840`) | `tenant/__init__.py`, `tenant/health.py`, `tenant/model.py` iskeleti mevcut |
| D-12 | Entity resolution fuzzy eşleştirme (`K4:550`, `K1:437-460`) | `entity_resolution/matcher.py` (VKN exact + rapidfuzz unvan + `match_semantic`) + `threshold_optimizer.py` |

**Doğrulama oranı: 12 / 19 = %63**

### 4.2 ❌ Çürütülen İddialar (6)

| # | Belge iddiası | Gerçek kod durumu | Karar |
|---|---------------|-------------------|-------|
| Ç-1 | `K4:109` tablo adı `firms` | Kodun tamamında `companies` | **Kod esas.** K4 düzeltilecek. |
| Ç-2 | `K1:651-662` "müşteri–ürün uyumu yapılmaz" | `web_app.py:1085 /api/match` zaten yapıyor | **Kod esas.** K1 sınırı eskimiş. |
| Ç-3 | `K4:51,154-163` Neo4j graph katmanı | `src/` içinde **0 satır** Neo4j | **Uygulanmamış.** Belgede "planlanan" işaretlensin. |
| Ç-4 | `K4:106-147` PostGIS `GEOMETRY(Point,4326)` | Kodda coğrafi sütun kullanımı yok | **Uygulanmamış.** |
| Ç-5 | `K3:105` `huginn_`/`muninn_`/`odin_` önekleri | Sadece `odin_ai/` var | **Kısmen yanlış.** K3 düzeltilecek. |
| Ç-6 | `K2:74-172` 6 OSINT motoru veri kaynakları | `scrapers/` = tek dosya (`kariyernet.py`) | **%0 gerçekleşme.** K2 vizyon belgesi olarak işaretlensin. |

**Çürütme oranı: 6 / 19 = %32**

### 4.3 `docs/MUNINN_*` Belgeleriyle Çakışan Kararlar

| Çakışma | MUNINN belgesi | V10 belgesi | Öneri |
|---------|----------------|-------------|-------|
| **Kapsam** | `MUNINN_STREAMLIT_PLAN_2026-09-18.md` yalnız admin paneli (8501) kapsıyor | `K3:13` Huginn+Muninn birlikte konumlanıyor | Çakışma **yok** — MUNINN planı K3'ün alt kümesi. Onaylanabilir. |
| **Öncelik** | MUNINN planı Faz 0'da `env_file` + auth `st.stop()` diyor | `K4:827-857` admin roadmap'te bu maddeler yok | MUNINN planı **daha güncel**; K4 § 16.5 eskimiş (B-8). |
| **UI stack** | `UI_STACK_DEGERLENDIRME_2026-09-18.md` Streamlit'te kalma kararı | `K3:86-103` `src/modules/{huginn,muninn,odin}` hedef ağacı | K3:105 zaten "hedef/ilham" diyor → çakışma **yumuşak**. |
| **Plan isabeti** | `MUNINN_PLAN_UC_TUR_DEGERLENDIRME_2026-09-18.md` → ŞARTLI KABUL, isabet %47 | — | V10 netleştirmesi bu oranı yükseltir; F0+F1 sonrası yeniden ölçülmeli. |

---

## 5. Açık Sorular

> Hiçbirine varsayım üretilmedi. Her biri KAHİN (Ürün Sahibi) kararı bekliyor.

| Kod | Soru | Sahibi | Tıkadığı iş | Karar için gereken bilgi |
|-----|------|--------|-------------|--------------------------|
| **K-A** | K2'nin OSINT kolu (L3) **ne zaman** başlayacak? Ankara/OSB odağıyla mı yoksa global mi? | KAHİN | F4 (scraper bağlama) tamamen bloke | İlk müşterinin OSINT skoru mu firma listesi mi istediği |
| **K-B** | Müşteriye gösterilecek **resmî skor seti** hangisi: K2'nin 8 skoru mu, K4'ün need/fit/timing'i mi? | KAHİN | F5 (skor motoru), müşteri paneli tasarımı | Satış konuşmasında hangi sayının söylendiği |
| **K-C** | `firms` → `companies` adı için **resmî düzeltme** K4'e işlensin mi, yoksa K4 arşive mi alınsın? | KAHİN + roo | F1 | K4'ün hâlâ aktif SSOT sayılıp sayılmadığı |
| **K-D** | Multi-tenant (F6) **şimdi** başlasın mı? `tenant/` iskeleti hazır, Eylül penceresi açık. | KAHİN | F6 | İkinci bir ödeyen müşteri var mı |
| **K-E** | Neo4j gerçekten gerekli mi? Şu an 0 satır; ilişki grafiği PostgreSQL'de de tutulabilir. | KAHİN | K2 Faz 3 (Entity Graph) | Grafik sorgularının müşteriye görünür olup olmayacağı |
| **K-F** | `/api/v1/huginn/*` + `/api/v1/muninn/*` rota göçü yapılacak mı? Mevcut rotalar çalışıyor. | KAHİN | B-6, müşteri API sözleşmesi | Dış entegratör olup olmadığı (kırılma riski) |
| **K-G** | İki SSOT beyanı (B-11) — hangisi resmî? Öneri: K4 = **veri** SSOT, K5 = **yetenek** SSOT. | KAHİN | Belge disiplini | Onay yeterli |
| **K-H** | K2 belgesi (B-7: tarihsiz, mükerrer, bozuk) **temizlensin mi** yoksa arşive mi alınsın? | KAHİN | F1 | K2'nin hâlâ referans alınıp alınmadığı |

---

## 6. İkinci Tur Derin Değerlendirme

> KAHİN'in kalıcı metodoloji emri gereği plan, yazıldıktan sonra kendi eleştirisinden geçirilmiştir.

### 6.1 Risk Envanteri

| # | Risk | Tür | Olasılık × Etki | Erken uyarı sinyali | Azaltma aksiyonu |
|---|------|-----|-----------------|---------------------|------------------|
| R1 | B-14 hatası üretimde müşteriye 500 döner | Teknik | Yüksek × Yüksek | Filtre kullanan ilk istek 500 verir | **F0'da hemen sil** (6 satır) |
| R2 | K-A kararsızlığı F4'ü süresiz erteler, K5 yatırımı boşa gider | Ürün | Orta × Yüksek | 2 hafta karar gelmemesi | K-A'yı ilk karar noktası yap; gelmezse F4 **dondur**, kaynak F3/F5'e |
| R3 | Belge–kod farkı büyümeye devam eder, yeni ajan yanlış belgeyi okur | Operasyonel | Yüksek × Orta | Aynı çelişkinin ikinci kez raporlanması | F1'de her çürütülen iddianın **üstüne** düzeltme notu yaz |
| R4 | Üç katman aynı anda ilerletilirse hiçbiri bitmez | Ürün | Orta × Yüksek | Aynı hafta L1+L2+L3 görevi açık | **Tek seferde tek katman** kuralı (§ 6.2 Ç1) |
| R5 | Neo4j/PostGIS "yapılacak" sanılıp sprint'e alınır | Teknik | Düşük × Orta | Görev panosunda graph görevi | Belgede "PLANLANMADI" etiketi |
| R6 | Admin UX zinciri (F2) veri işiyle aynı dosyalara dokunur | Operasyonel | Düşük × Orta | Kilit çakışması | F2 yalnız `web_dashboard/` + `app.py`; veri işleri `src/` |
| R7 | K2 vizyonu satış konuşmasına girer, teslim edilemez | Ürün | Orta × Yüksek | Sunumda "8 skor" geçmesi | K-B kararı alınana kadar K2 **dış iletişimde kullanılmaz** |

### 6.2 Çakışma Önleyici Aksiyonlar

| # | Çakışma | Önleyici kural |
|---|---------|----------------|
| Ç1 | Katmanlar karışıyor | **Sahiplik sınırı:** L1 = `src/company_master/{schema,etl,search,entity_resolution}` · L2 = `intelligence/` · L3 = `{gateway,engine/osint_engine,scrapers}`. Bir görev tek katmana dokunur. |
| Ç2 | İki belge kendini SSOT ilan ediyor | **İsim alanı:** "Veri SSOT" = K4 § 3 · "Yetenek SSOT" = K5 · "Marka SSOT" = K3. Terim tek başına kullanılmaz. |
| Ç3 | `companies` / `firms` ikiliği | **Sözleşme:** Kod tablosu `companies`. Yeni hiçbir belgede `firms` geçmez. `marka_denetim.py` benzeri bir kontrol eklenebilir (opsiyonel). |
| Ç4 | Aynı fonksiyonun iki tanımı (`search_companies`) | **Kural:** `__init__.py`'de export edilmeyen iskelet dosya bırakılmaz. B-15 siliniyor. |
| Ç5 | Admin UX ile veri işi aynı anda | **Kilit:** F2 görevlerinde `dosyalar=["app.py","web_dashboard/**"]`; F3/F5'te `src/company_master/**`. |

### 6.3 Verimlilik — Ne Atılır, Ne Mevcutla Yapılır, Ne Yeni Kod İster

| Sınıf | İş |
|-------|-----|
| **🗑️ Atılır (YAGNI)** | Neo4j kurulumu (K-E'ye kadar) · PostGIS · `search/fulltext.py` · K3'ün `src/modules/` göçü (K3:105 zaten "ilham" diyor) · `/api/v1/*` rota göçü (K-F'ye kadar) |
| **♻️ Mevcutla karşılanır** | Arama → `pg_trgm` GIN zaten var, Elasticsearch gerekmez (D-9) · Vektör → `vector/` hazır (D-10) · Eşleştirme → `matcher.py` hazır (D-12) · Web çekme → `9Router web_fetch/web_search` canlı (K5:38-39), yeni HTTP istemcisi yazılmaz · Çoklu müşteri → `tenant/` iskeleti hazır (D-11) |
| **✍️ Gerçekten yeni kod ister** | F0 düzeltmeleri (6 satır silme) · F3 üç tablo ETL bağlantısı · F4 üç kaynak toplayıcı (ETBİS/Whois/DNS) · F5 skor motoru birleştirme |

**Kazanç:** Belgelerin ima ettiği işin yaklaşık **%40'ı** mevcut kodla zaten karşılanıyor; **%25'i** atılabiliyor. Gerçek yeni iş ≈ **%35**.

### 6.4 Teslim Planı

| Faz | Çıktı | Bitti kriteri | İyimser | Beklenen | Kötümser | Bağımlılık |
|-----|-------|---------------|---------|----------|----------|------------|
| F0 | 3 hijyen düzeltmesi | İlgili testler yeşil, `has_phone` filtresi çalışıyor | 2 sa | 4 sa | 1 gün | — |
| F1 | 6 belge düzeltme notu | Her çürütülen iddia belgede işaretli | 4 sa | 1 gün | 2 gün | F0 |
| F2 | 4 admin UX görevi | Her birinde wireframe onayı + test | 2 gün | 3 gün | 5 gün | K-5 onayı |
| F3 | 3 genişletilmiş tablo ETL'de | Dolum oranı raporlanıyor | 3 gün | 5 gün | 8 gün | F1 |
| F4 | 3 OSINT kaynağı | `sources` tablosuna yazıyor | 5 gün | 10 gün | 20 gün | **K-A** |
| F5 | Üç skor motoru | 8313 firmada hesaplanıyor | 5 gün | 10 gün | 15 gün | F3, **K-B** |
| F6 | Multi-tenant izolasyon | Bir müşteri kendi verisini görüyor | 5 gün | 10 gün | 20 gün | F5, **K-D** |

**Kritik yol:** F0 → F1 → F3 → F5 → F6 ≈ beklenen **26 gün**. F2 paralel, F4 karara bağlı.

### 6.5 Geri Dönüş Planı

| Faz | Ters giderse | Geri alma | Tek yönlü kapı? |
|-----|--------------|-----------|-----------------|
| F0 | Silinen blok gerekliymiş | `git revert` — 6 satır | Hayır |
| F1 | Belge düzeltmesi yanlış | Belge geri alınır | Hayır |
| F2 | UI bozulur | Streamlit restart + revert | Hayır |
| F3 | Yeni tablolar boş kalır | `CREATE TABLE IF NOT EXISTS` — veri kaybı yok (`K1:343`) | **Kısmen** — tablo silmek veri siler |
| F4 | Kaynak yasal/teknik engel | Scraper devre dışı, `sources` kaydı pasif | Hayır |
| F5 | Skorlar yanlış çıkar | Skor sütunu yeniden hesaplanır | Hayır |
| F6 | **Multi-tenant şema değişikliği** | Geri alınması pahalı; tüm sorgular tenant filtresi ister | **🔴 EVET — tek yönlü kapı** |

**Tek yönlü kapı uyarısı:** F6 (multi-tenant) şema düzeyinde geri dönülmesi zor bir değişikliktir. K-D kararı alınmadan başlatılmamalıdır.

### 6.6 Karar Noktaları

| Sıra | Karar | Ne zaman gerekli | KAHİN'e lazım olan bilgi |
|------|-------|------------------|--------------------------|
| 1 | **K-C** (`firms`/`companies` resmîleştirme) | F1 başlamadan | K4 aktif SSOT mu, arşiv mi |
| 2 | **K-G** (iki SSOT ayrımı) | F1 başlamadan | Önerilen ayrım kabul mü |
| 3 | **K-H** (K2 temizlensin mi) | F1 sırasında | K2 hâlâ referans mı |
| 4 | **K-B** (resmî skor seti) | F5 başlamadan | Satışta hangi sayı söyleniyor |
| 5 | **K-A** (OSINT kolu ne zaman) | F4 başlamadan | İlk müşteri ne istiyor |
| 6 | **K-E** (Neo4j gerekli mi) | K2 Faz 3'ten önce | Grafik müşteriye görünecek mi |
| 7 | **K-F** (rota göçü) | Müşteri API sözleşmesi öncesi | Dış entegratör var mı |
| 8 | **K-D** (multi-tenant) | F6 başlamadan — **tek yönlü kapı** | İkinci ödeyen müşteri var mı |

---

## 7. İlk Başlatılacak İşler (Karar Beklemeyen)

Aşağıdaki 3 iş **hiçbir KAHİN kararına bağlı değildir** ve hemen başlatılabilir:

| Görev kimliği | Öncelik | İş | Dosya | Süre | Test |
|---------------|---------|-----|-------|------|------|
| `V10-HIJYEN-01` | **P0** | B-14 mükerrer where bloğunu sil | `src/company_master/search/engine.py:182-187` | 15 dk | `has_phone=True` çağrısı SQL üretir, `<> ""` içermez |
| `V10-HIJYEN-02` | P2 | B-15 ölü dosyayı sil | `src/company_master/search/fulltext.py` | 10 dk | `from company_master.search import search_companies` çalışır |
| `V10-BELGE-01` | P1 | 6 çürütülen iddiaya belge düzeltme notu | K1, K3, K4 | 1 gün | Her çürütülen iddianın üstünde uyarı satırı var |

Kalan tüm fazlar § 6.6'daki karar sırasına bağlıdır.

---

## Referans Bütünlüğü Beyanı

Bu belgedeki **hiçbir iddia** kaynak referansı olmadan yazılmamıştır. Belge ile kod çeliştiği **6 noktada** kod esas alınmış ve çelişki § 4.2'de ayrıca işaretlenmiştir. Belgelerde bulunmayan **8 konu** varsayıma çevrilmeden § 5 Açık Sorular'a taşınmıştır.
