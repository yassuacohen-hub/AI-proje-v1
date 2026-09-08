# Ajanlar ve Gelişime Açık Yapı

Bu bölüm, proje içindeki yapay zeka ajanlarının sorumluluk alanlarını, sınırlarını ve gelişime açık yapısını açıklar.

## Temel ilke

- Her ajan tek bir ana sorumluluğa sahip olmalıdır.
- Ajanlar birbirini ezmemeli, aynı anda aynı işi yapmamalıdır.
- Gelişim açık olmalı; ancak riskli operasyonlar kontrollü ve kısıtlı şekilde çalıştırılmalıdır.
- Web kazıma ve veri toplama, ayrı uzmanluk alanı olarak eklenebilir; ana karar ve doğrulama katmanı ayrı tutulmalıdır.

## Ajan seti

1. [[01_koordinator_ajan]]
2. [[02_mimar_ajan]]
3. [[03_arastirmaci_ajan]]
4. [[04_gelistirici_ajan]]
5. [[05_kalite_ajan]]
6. [[06_web_kazima_uzmani]]

## 8. OSINT Uzmanlık Rolü (Tüm Ajanlara Ortak Referans Görev)

Tüm iç ajanlar ve harici ajanlar, aşağıdaki OSINT rol tanımını kendi uzmanlık alanlarına ek olarak referans görev olarak uygular.

- **OSINT Rol Tanımı:** [[09_osint_rol_tanimi]]

### 8.1 Kapsam

- OSINT (Open Source Intelligence), Kurumsal Risk Analizi, Dolandırıcılık Tespiti (Fraud Detection), KYC (Know Your Customer) ve Vendor Due Diligence.
- Her ajan, verilen bir şirket/alan adı/web sitesi hakkında açık kaynak istihbaratı toplamak, doğrulamak, ilişkilendirmek ve analiz etmekle yükümlüdür.

### 8.2 Tüm Ajanlara Tanımlı Alt Görevler

- Web Kazıma Uzmanı -> 09_osint_rol_tanimi.md (footer VKN, MERSİS, sosyal medya kesfi)
- Arastirmaci -> 09_osint_rol_tanimi.md (kaynak dogrulama, guven seviyesi)
- Mimar -> 09_osint_rol_tanimi.md (guvenlik/itibar modeli mimarisi)
- Gelistirici -> 09_osint_rol_tanimi.md (schema/OSINT alanlari)
- Kalite -> 09_osint_rol_tanimi.md (guven seviyesi dogrulamasi)
- Koordinator -> 09_osint_rol_tanimi.md (OSINT gorev dagitimi)
- Harici ajanlar -> 09_osint_rol_tanimi.md (brief'lere OSINT gorev tipleri eklenir)

## Ajanlar için standart

- Her ajan için temel alanlar şunlardır:
  - Amaç
  - Sorumluluk alanı
  - Kısıtlar
  - Çalıştığı dosyalar
  - Çıktı formatı
  - Gelişim ve genişletme alanları

## Önerilen operasyon modeli

- Koordinatör ajan yönlendirir.
- Mimar ajan tasarımı korur.
- Araştırmacı ajan bilgi toplar.
- Geliştirici ajan kod üretir.
- Kalite ajan doğrulama yapar.
- Web kazıma uzmanı sadece veri temini için kullanılır.

Bu yapı, hem genişletilebilir hem de denetlenebilir bir yapıdır.

---

## 7. Harici Ajanlar (External Agents)

İç ajan setine ek olarak, proje dışından gelen yapay zeka ajanları (Cursor Grok, GitHub Copilot, Claude Code vb.) kontrollü şekilde projeye dahil edilebilir.

- **Protokol:** [[07_harici_ajan_protokolu]]
- **Görev Önerileri:** [[08_harici_ajan_gorev_onerileri]]

### 7.1 Temel Farklar

| Özellik | İç Ajan (01–06) | Harici Ajan |
|---------|-----------------|-------------|
| Erişim | Proje kökü + workspace | Yalnız `workspace/external/{agent_id}/` |
| Görev tipi | Uzmanlık alanına göre sabit | Brief ile tanımlı 6 tipten biri |
| Doğrulama | Kalite ajanı + orkestratör | Orkestratör + kalite ajanı + insan onayı |
| Gizli veri | Kısıtlı erişim, kurallara bağlı | **Asla** erişemez |

### 7.2 Harici Ajan Kategorileri

- **Cursor Grok** — hızlı kod analizi, Streamlit/Python optimizasyonu, test üretimi.
- **GitHub Copilot** — snippet, boilerplate, CI/CD şablonları.
- **Claude Code / diğer LLM ajanlar** — mimari dokümantasyon, teknik borç analizi, güvenlik audit.

### 7.3 Koordinasyon

- Tüm harici ajan görevleri **orkestratör ([[01_koordinator_ajan]]) üzerinden** yürütülür.
- Başarısızlık durumunda 3 deneme sonrası iç ajanlara reassign yapılır.
- Hata kayıtları `AGENT_SYNC.md` → "ErrorLedger" bölümüne yazılır.