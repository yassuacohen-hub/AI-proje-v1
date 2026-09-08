# 07 - Harici Ajan Entegrasyon Protokolü

Bu belge, **Cursor Grok, GitHub Copilot, Claude Code** ve benzeri dış yapay zeka ajanlarının proje orkestratörüyle güvenli ve kontrollü biçimde haberleşmesini tanımlar. İç ajan seti ([[01_koordinator_ajan]] … [[06_web_kazima_uzmani]]) projeye doğrudan erişirken, harici ajanlar **yalnızca kendilerine ayrılmış workspace** üzerinden çalışır.

---

## 1. Amaç

- Harici ajanları (Cursor Grok, Copilot, Claude Code vb.) proje geliştirme döngüsüne kontrollü şekilde dahil etmek.
- Orkestratör ajanın ([[01_koordinator_ajan]]) harici ajanlara **görev paketi** göndermesini, dönen çıktıyı **okumasını, doğrulamasını** ve projeye **entegre etmesini** sağlamak.
- Proje kökünün, gizli verilerin ve ana şemaların harici ajanlardan **izole** kalmasını garanti etmek.
- KVKK, gizli anahtar ve üretim verisinin harici ajana sızmasını engellemek.

---

## 2. İzolasyon Prensibi

| Kural | Açıklama |
|-------|----------|
| Köke dokunma yasağı | Harici ajanlar proje köküne (`Huginn Data Insights/`) doğrudan yazma/okuma yetkisi **alamaz**. |
| Ayrılmış workspace | Her harici ajan yalnızca `workspace/external/{agent_id}/` altında çalışır (örn. `workspace/external/cursor_grok/`). |
| Gizli dosya yasağı | `.env`, `*.pem`, `*.key`, `secrets/`, `config/secrets.yaml` ve benzeri dosyalar harici ajana **asla** gösterilmez. |
| Şema yasağı | `db/schema/`, `src/company_master/schema/migrations/` ve üretim şeması harici ajana **gönderilmez**; sadece anonimleştirilmiş/sentetik şema özeti verilir. |
| Salt okunur bağlam | Harici ajana verilen kod dosyaları **salt okunur** olarak bağlanır; yazma yalnızca workspace içinde serbesttir. |

### 2.1 Workspace Yapısı (Önerilen)

```
workspace/
  external/
    cursor_grok/
      brief.md           # orkestratörden gelen görev paketi
      context/           # sadece bu görev için seçilmiş dosyalar
      output/            # harici ajanın ürettiği kod/doküman
      notes.md           # ajanın kendi notları (orquestratör tarafından okunabilir)
    copilot/
      ...
    claude_code/
      ...
```

---

## 3. İletişim Protokolü

### 3.1 Orkestratör → Harici Ajan (Gidiş)

Görev paketi **JSON** veya **Markdown brief** formatında hazırlanır. Minimum alanlar:

```json
{
  "agent_id": "cursor_grok",
  "task_id": "TSK-2026-09-02-001",
  "task_type": "code_review | refactoring | test_generation | documentation | data_transformation | research",
  "title": "app.py Streamlit performans optimizasyonu",
  "brief_path": "workspace/external/cursor_grok/brief.md",
  "context_files": [
    "src/etl/app.py"
  ],
  "constraints": {
    "no_db_schema_access": true,
    "no_env_access": true,
    "write_only_to": "workspace/external/cursor_grok/"
  },
  "success_criteria": [
    "Pagination eklendi (50/sayfa)",
    "st.cache_data ile DB cache"
  ],
  "deadline": "2026-09-03T18:00:00+03:00"
}
```

### 3.2 Harici Ajan → Orkestratör (Dönüş)

Harici ajan yalnızca `workspace/external/{agent_id}/output/` altına yazar. Dönüş özeti `notes.md` içinde yer alır:

```markdown
# Görev Sonucu — TSK-2026-09-02-001
- Durum: success | partial | failed
- Üretilen dosyalar:
  - output/app.py.optimized
  - output/pagination_patch.diff
- Öneriler:
  - ...
- Bilinen kısıtlar / varsayımlar:
  - ...
```

### 3.3 Orkestratörün Entegrasyon Adımları

1. Harici ajanın `output/` klasörünü oku.
2. Üretilen dosyaları **diff/review** ile kontrol et.
3. Kalite ajanı ([[05_kalite_ajan]]) ile sözleşme testi / tip kontrolü çalıştır.
4. Onay sonrası projedeki asıl yola **PR/branch** üzerinden uygula.
5. Durumu `AGENT_SYNC.md` → "Tamamlananlar" bölümüne yaz.

---

## 4. Güvenlik

- **.env ve gizli anahtarlar** harici ajana gönderilmez; bağlam dosyaları `grep -E "(API_KEY|SECRET|TOKEN|PASSWORD)"` ile taranır.
- **KVKK kapsamındaki veriler** (gerçek firma unvanı, telefon, e-posta, VKN) ham haliyle gönderilmez; anonimleştirilmiş/sentetik örnekler kullanılır.
- **Üretim veritabanı** bağlantısı harici ajana hiçbir koşulda verilmez; yalnızca salt okunur sandbox veya sentetik veri seti kullanılır.
- Tüm dosya erişimi **Orchestrator üzerinden** yönlendirilir; harici ajanın doğrudan kök erişimi yoktur.
- Workspace'e yazılan her dosya `git diff` ile gözden geçirilmeden ana dala alınmaz.
- Harici ajan çıktısı **güvenilir değildir**; her zaman kalite ajanı + insan onayı döngüsünden geçer.

---

## 5. Harici Ajanlara Özel Görev Tipleri

| # | Görev Tipi | Açıklama | Tipik Çıktı |
|---|-----------|----------|-------------|
| 1 | **Code Review** | Mevcut kodları gözden geçirme, iyileştirme önerileri | `output/review.md`, `output/suggestions.diff` |
| 2 | **Refactoring** | Kod optimizasyonu, design pattern uyumu | `output/refactored_*.py`, `output/refactor_notes.md` |
| 3 | **Test Üretme** | Unit test, integration test senaryoları | `output/test_*.py`, `output/coverage_report.md` |
| 4 | **Dokümantasyon** | README, yorum, API dökümanları | `output/README.md`, `output/API.md` |
| 5 | **Veri Dönüşümü** | CSV/JSON dönüşümleri, migration helper | `output/transform_*.py`, `output/sample.csv` |
| 6 | **Araştırma** | Teknoloji karşılaştırma, benchmark | `output/research.md`, `output/comparison_table.md` |

> Not: Veri tabanı şeması yazma, üretim migration uygulama ve gizli anahtar yönetimi **harici ajanlara verilmez**.

---

## 6. Hata Yönetimi

- Harici ajan başarısız olursa orkestratör **otomatik retry** yapar.
- Aynı `task_id` için **maksimum 3 deneme**.
- 3 başarısızlık sonrası görev **iç ajanlara** (örn. [[04_gelistirici_ajan]]) **reassign** edilir.
- Her hata kaydı `AGENT_SYNC.md` → "ErrorLedger" bölümüne yazılır:
  - `task_id`, `agent_id`, hata tipi, hata mesajı, deneme sayısı, alınan aksiyon.

### 6.1 ErrorLedger Şeması

| task_id | agent_id | tarih | hata_tipi | hata_mesajı | deneme | aksiyon |
|---------|----------|-------|-----------|-------------|--------|---------|
| TSK-… | cursor_grok | 2026-09-02 | timeout | LLM timeout 60s | 3/3 | iç ajana reassign |

---

## 7. Görev Tiplerine Göre Workspace Politikası

| Görev Tipi | Okuma Hakkı | Yazma Hakkı | Özel Kısıt |
|-----------|-------------|-------------|-----------|
| Code Review | salt okunur | yasak | yalnız `output/review.md` |
| Refactoring | salt okunur | yalnız `output/` | üretim yoluna doğrudan yazamaz |
| Test Üretme | salt okunur | yalnız `output/` | orijinal testleri silemez |
| Dokümantasyon | salt okunur | yalnız `output/` | README şablonuna uymalı |
| Veri Dönüşümü | sentetik veri | yalnız `output/` | gerçek veri yasak |
| Araştırma | salt okunur | yalnız `output/` | dış ağ çağrısı kontrollü |

---

## 8. Operasyon Akışı (Özet)

```
[Kullanıcı / Roadmap]
        |
        v
[01 Koordinatör] — görev tipine göre iç/harici ajan seçer
        |  (harici ise)
        v
[Brief + Context] -> workspace/external/{agent_id}/
        |
        v
[Harici Ajan] — yalnız kendi workspace'inde çalışır
        |
        v
[Output + Notes] — workspace/external/{agent_id}/output/
        |
        v
[01 Koordinatör] — diff/review + [05 Kalite] doğrulaması
        |  (başarılı ise)
        v
[Ana şube / PR] — kalıcı entegrasyon
        |
        v
[AGENT_SYNC.md] — Tamamlananlar + ErrorLedger güncellenir
```

---

## 9. Kaynaklar

- [[AGENT_SYNC]]
- [[AI proje v1/AGENTS]]
- [[V10/09_kurallar_ve_promptlar/02_calisma_kurallari]]
- [[V10/08-Ajanlar/08_harici_ajan_gorev_onerileri]]
- Ana bağlam: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`